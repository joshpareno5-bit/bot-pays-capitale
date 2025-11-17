#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bot Telegram pour un quiz sur les pays et capitales du monde.
"""

import logging
import random
import os
import asyncio

from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    MenuButtonCommands,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler,
)

# --- Configuration ---

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY") 
if not TELEGRAM_API_KEY:
    raise ValueError("La variable d'environnement TELEGRAM_API_KEY n'est pas définie !")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Données des pays et capitales ---
COUNTRIES_DATA = [
    {'continent': 'Europe', 'pays': 'France', 'capitale': 'Paris', 'population': 68},
    {'continent': 'Europe', 'pays': 'Allemagne', 'capitale': 'Berlin', 'population': 83},
    {'continent': 'Europe', 'pays': 'Italie', 'capitale': 'Rome', 'population': 59},
    {'continent': 'Europe', 'pays': 'Espagne', 'capitale': 'Madrid', 'population': 47},
    {'continent': 'Europe', 'pays': 'Royaume-Uni', 'capitale': 'Londres', 'population': 67},
    {'continent': 'Amérique', 'pays': 'États-Unis', 'capitale': 'Washington', 'population': 331},
    {'continent': 'Amérique', 'pays': 'Canada', 'capitale': 'Ottawa', 'population': 38},
    {'continent': 'Amérique', 'pays': 'Brésil', 'capitale': 'Brasilia', 'population': 214},
    {'continent': 'Amérique', 'pays': 'Argentine', 'capitale': 'Buenos Aires', 'population': 45},
    {'continent': 'Amérique', 'pays': 'Mexique', 'capitale': 'Mexico', 'population': 128},
    {'continent': 'Asie', 'pays': 'Chine', 'capitale': 'Pékin', 'population': 1402},
    {'continent': 'Asie', 'pays': 'Japon', 'capitale': 'Tokyo', 'population': 126},
    {'continent': 'Asie', 'pays': 'Inde', 'capitale': 'New Delhi', 'population': 1380},
    {'continent': 'Asie', 'pays': 'Russie', 'capitale': 'Moscou', 'population': 144},
    {'continent': 'Asie', 'pays': 'Corée du Sud', 'capitale': 'Séoul', 'population': 52},
    {'continent': 'Afrique', 'pays': 'Nigeria', 'capitale': 'Abuja', 'population': 206},
    {'continent': 'Afrique', 'pays': 'Égypte', 'capitale': 'Le Caire', 'population': 104},
    {'continent': 'Afrique', 'pays': 'Afrique du Sud', 'capitale': 'Pretoria', 'population': 60},
    {'continent': 'Afrique', 'pays': 'Kenya', 'capitale': 'Nairobi', 'population': 54},
    {'continent': 'Afrique', 'pays': 'Maroc', 'capitale': 'Rabat', 'population': 37},
    {'continent': 'Océanie', 'pays': 'Australie', 'capitale': 'Canberra', 'population': 26},
    {'continent': 'Océanie', 'pays': 'Nouvelle-Zélande', 'capitale': 'Wellington', 'population': 5},
]

# --- États de la conversation ---
SELECTING_MODE, SELECTING_TYPE, IN_QUIZ, REVISION_MODE = range(4)
BEST_SCORE_KEY = 'best_survival_score'

# --- Fonctions auxiliaires ---
def get_main_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎓 Mode Découverte"), KeyboardButton("🎯 Mode Défi (20 questions)")],
        [KeyboardButton("☠️ Mode Survie"), KeyboardButton("📚 Mode Révision")],
        [KeyboardButton("🏆 Meilleur score"), KeyboardButton("❓ Aide")]
    ], resize_keyboard=True, one_time_keyboard=False)

def get_quiz_type_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Capitale → Pays"), KeyboardButton("Pays → Capitale")],
        [KeyboardButton("🔙 Retour au menu")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_quiz_control_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🏁 Arrêter le quiz")]
    ], resize_keyboard=True, one_time_keyboard=False)

def get_revision_control_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔙 Retour au menu")]
    ], resize_keyboard=True, one_time_keyboard=False)

def generate_question_text(context: CallbackContext) -> str:
    user_data = context.user_data
    question_data = user_data['current_question']
    question_type = user_data['question_type']
    score = user_data.get('score', 0)
    question_count = user_data.get('question_count', 0)
    
    mode_text = {
        'discovery': "Découverte",
        'challenge': f"Défi (Question {question_count}/20)",
        'survival': "Survie"
    }.get(user_data['mode'], "")
    
    text = f"🕹️ <b>Mode: {mode_text}</b> | 🎯 <b>Score: {score}</b>\n\n"
    
    if question_type == 'pays_capitale':
        text += f"Quelle est la capitale du pays : <b>{question_data['pays']}</b> ?"
    else:  # capitale_pays
        text += f"De quel pays est la capitale : <b>{question_data['capitale']}</b> ?"
        
    return text

def generate_options(context: CallbackContext):
    user_data = context.user_data
    correct_data = user_data['current_question']
    question_type = user_data['question_type']
    
    # Générer 3 mauvaises réponses
    wrong_options = []
    all_options = [d for d in COUNTRIES_DATA if d != correct_data]
    
    while len(wrong_options) < 3 and all_options:
        wrong_option = random.choice(all_options)
        all_options.remove(wrong_option)
        
        if question_type == 'pays_capitale':
            wrong_options.append(wrong_option['capitale'])
        else:
            wrong_options.append(wrong_option['pays'])
    
    # Créer la liste des options
    if question_type == 'pays_capitale':
        correct_answer = correct_data['capitale']
    else:
        correct_answer = correct_data['pays']
    
    options = wrong_options + [correct_answer]
    random.shuffle(options)
    
    user_data['correct_answer'] = correct_answer
    user_data['options'] = options
    
    return options

# --- Commandes de base ---
async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    best_score = context.bot_data.get(BEST_SCORE_KEY, 0)
    
    welcome_message = (
        f"🌍 <b>Bienvenue {user.first_name} !</b> 🌍\n\n"
        "Testez vos connaissances sur les pays et capitales du monde !\n\n"
        "Choisissez un mode de jeu pour commencer :\n\n"
        f"🏆 <i>Meilleur score (Survie) : {best_score}</i>"
    )
    
    # Configurer le menu de commandes
    await context.bot.set_my_commands([
        ("start", "Démarrer le bot"),
        ("help", "Afficher l'aide"),
        ("score", "Voir le meilleur score")
    ])
    
    await update.message.reply_text(
        text=welcome_message,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )
    return SELECTING_MODE

async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "📚 <b>Aide du Bot Pays & Capitales</b>\n\n"
        "🎓 <b>Mode Découverte</b> : Jouez autant que vous voulez\n"
        "🎯 <b>Mode Défi</b> : 20 questions chronométrées\n"
        "☠️ <b>Mode Survie</b> : Une erreur et c'est terminé !\n"
        "📚 <b>Mode Révision</b> : Consultez la base de données\n\n"
        "Utilisez les boutons pour naviguer. Bonne chance ! 🍀"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def show_best_score(update: Update, context: CallbackContext) -> None:
    best_score = context.bot_data.get(BEST_SCORE_KEY, 0)
    await update.message.reply_text(
        f"🏆 <b>Meilleur score en mode Survie : {best_score}</b>",
        parse_mode='HTML'
    )

# --- Gestion des modes ---
async def handle_mode_selection(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    user_data = context.user_data
    
    if user_text == "🎓 Mode Découverte":
        user_data['mode'] = 'discovery'
        await update.message.reply_text(
            "Vous avez choisi le mode <b>Découverte</b> !\nChoisissez le type de questions :",
            reply_markup=get_quiz_type_keyboard(),
            parse_mode='HTML'
        )
        return SELECTING_TYPE
        
    elif user_text == "🎯 Mode Défi (20 questions)":
        user_data['mode'] = 'challenge'
        user_data['total_questions'] = 20
        await update.message.reply_text(
            "Vous avez choisi le mode <b>Défi</b> (20 questions) !\nChoisissez le type de questions :",
            reply_markup=get_quiz_type_keyboard(),
            parse_mode='HTML'
        )
        return SELECTING_TYPE
        
    elif user_text == "☠️ Mode Survie":
        user_data['mode'] = 'survival'
        await update.message.reply_text(
            "Vous avez choisi le mode <b>Survie</b> !\nUne erreur = Game Over !\nChoisissez le type de questions :",
            reply_markup=get_quiz_type_keyboard(),
            parse_mode='HTML'
        )
        return SELECTING_TYPE
        
    elif user_text == "📚 Mode Révision":
        await update.message.reply_text(
            "📚 <b>Mode Révision</b>\n\n"
            "Tapez le nom d'un pays ou d'une capitale pour obtenir des informations.\n"
            "Exemple : 'France' ou 'Paris'",
            reply_markup=get_revision_control_keyboard(),
            parse_mode='HTML'
        )
        return REVISION_MODE
        
    elif user_text == "🏆 Meilleur score":
        await show_best_score(update, context)
        return SELECTING_MODE
        
    elif user_text == "❓ Aide":
        await help_command(update, context)
        return SELECTING_MODE
    
    else:
        await update.message.reply_text("Veuillez choisir une option valide dans le menu.")
        return SELECTING_MODE

async def handle_quiz_type_selection(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    user_data = context.user_data
    
    if user_text == "🔙 Retour au menu":
        await update.message.reply_text(
            "Retour au menu principal :",
            reply_markup=get_main_menu_keyboard()
        )
        return SELECTING_MODE
        
    elif user_text in ["Pays → Capitale", "Capitale → Pays"]:
        user_data['question_type'] = 'pays_capitale' if user_text == "Pays → Capitale" else 'capitale_pays'
        user_data['score'] = 0
        user_data['question_count'] = 0
        user_data['asked_questions'] = []
        
        return await send_question(update, context)
    
    else:
        await update.message.reply_text("Veuillez choisir un type de question valide.")
        return SELECTING_TYPE

# --- Gestion du quiz ---
async def send_question(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    
    # Vérifier si on a épuisé toutes les questions (mode défi)
    if user_data['mode'] == 'challenge' and user_data['question_count'] >= user_data['total_questions']:
        return await end_quiz(update, context)
    
    # Choisir une question non posée
    available_questions = [q for q in COUNTRIES_DATA if q['pays'] not in user_data['asked_questions']]
    if not available_questions:
        # Si plus de questions disponibles, réinitialiser
        user_data['asked_questions'] = []
        available_questions = COUNTRIES_DATA.copy()
    
    question_data = random.choice(available_questions)
    user_data['current_question'] = question_data
    user_data['asked_questions'].append(question_data['pays'])
    user_data['question_count'] += 1
    
    # Générer les options
    options = generate_options(context)
    
    # Créer le clavier avec les options
    keyboard_buttons = [[KeyboardButton(option)] for option in options]
    keyboard_buttons.append([KeyboardButton("🏁 Arrêter le quiz")])
    reply_markup = ReplyKeyboardMarkup(keyboard_buttons, resize_keyboard=True, one_time_keyboard=True)
    
    # Envoyer la question
    question_text = generate_question_text(context)
    await update.message.reply_text(
        text=question_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return IN_QUIZ

async def handle_answer(update: Update, context: CallbackContext) -> int:
    user_answer = update.message.text
    user_data = context.user_data
    
    if user_answer == "🏁 Arrêter le quiz":
        return await end_quiz(update, context)
    
    correct_answer = user_data['correct_answer']
    is_correct = (user_answer == correct_answer)
    
    # Feedback immédiat
    if is_correct:
        user_data['score'] = user_data.get('score', 0) + 1
        feedback = f"✅ <b>Correct !</b> La réponse était bien : {correct_answer}"
    else:
        feedback = f"❌ <b>Incorrect !</b> La bonne réponse était : {correct_answer}"
    
    await update.message.reply_text(feedback, parse_mode='HTML')
    
    # Gestion du mode survie
    if user_data['mode'] == 'survival' and not is_correct:
        score = user_data.get('score', 0)
        best_score = context.bot_data.get(BEST_SCORE_KEY, 0)
        
        if score > best_score:
            context.bot_data[BEST_SCORE_KEY] = score
            best_score = score
        
        await asyncio.sleep(2)
        
        game_over_text = (
            f"☠️ <b>GAME OVER</b> ☠️\n\n"
            f"Votre score final : {score}\n"
            f"Meilleur score : {best_score}\n\n"
            "Essayez encore !"
        )
        
        await update.message.reply_text(
            text=game_over_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='HTML'
        )
        return SELECTING_MODE
    
    await asyncio.sleep(1.5)
    return await send_question(update, context)

async def end_quiz(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    score = user_data.get('score', 0)
    total = user_data.get('question_count', 0)
    
    # Calculer le pourcentage
    percentage = (score / total * 100) if total > 0 else 0
    
    end_text = (
        f"🎉 <b>Quiz terminé !</b> 🎉\n\n"
        f"Score final : {score}/{total}\n"
        f"Pourcentage de réussite : {percentage:.1f}%\n\n"
        "Choisissez un nouveau mode pour rejouer :"
    )
    
    await update.message.reply_text(
        text=end_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )
    
    return SELECTING_MODE

# --- Mode Révision ---
async def handle_revision_search(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    
    if user_text == "🔙 Retour au menu":
        await update.message.reply_text(
            "Retour au menu principal :",
            reply_markup=get_main_menu_keyboard()
        )
        return SELECTING_MODE
    
    search_term = user_text.lower().strip()
    results = []
    
    for country in COUNTRIES_DATA:
        if (search_term in country['pays'].lower() or 
            search_term in country['capitale'].lower() or
            search_term in country['continent'].lower()):
            results.append(country)
    
    if results:
        message = "🔎 <b>Résultats de recherche :</b>\n\n"
        for result in results:
            message += (
                f"🏴 <b>{result['pays']}</b>\n"
                f"🏛️ Capitale : {result['capitale']}\n"
                f"🌍 Continent : {result['continent']}\n"
                f"👥 Population : {result['population']} millions\n\n"
            )
    else:
        message = "❌ Aucun résultat trouvé. Essayez avec un autre nom."
    
    await update.message.reply_text(
        text=message,
        reply_markup=get_revision_control_keyboard(),
        parse_mode='HTML'
    )
    
    return REVISION_MODE

# --- Fonction principale ---
def main() -> None:
    # Vérifier que le token est bien défini
    if not TELEGRAM_API_KEY:
        logger.error("TELEGRAM_API_KEY n'est pas définie !")
        return
    
    application = Application.builder().token(TELEGRAM_API_KEY).build()
    
    # Gestionnaire de conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mode_selection)
            ],
            SELECTING_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_type_selection)
            ],
            IN_QUIZ: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
            ],
            REVISION_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_revision_search)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    # Commandes supplémentaires
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('score', show_best_score))
    application.add_handler(conv_handler)
    
    # Configuration pour le déploiement
    PORT = int(os.environ.get("PORT", 8443))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
    
    if RENDER_EXTERNAL_URL:
        # Mode webhook pour Render
        logger.info(f"Démarrage avec webhook sur {RENDER_EXTERNAL_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{RENDER_EXTERNAL_URL}/webhook"
        )
    else:
        # Mode polling pour le développement
        logger.info("Démarrage en mode polling...")
        application.run_polling()

if __name__ == '__main__':
    main()