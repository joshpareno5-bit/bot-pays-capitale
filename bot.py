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
    # // Afrique
    {"continent": "Afrique", "pays": "Algérie", "capitale": "Alger", "population": 43},
    {"continent": "Afrique", "pays": "Angola", "capitale": "Luanda", "population": 33},
    {"continent": "Afrique", "pays": "Bénin", "capitale": "Porto-Novo", "population": 12},
    {"continent": "Afrique", "pays": "Botswana", "capitale": "Gaborone", "population": 2.4},
    {"continent": "Afrique", "pays": "Burkina Faso", "capitale": "Ouagadougou", "population": 21},
    {"continent": "Afrique", "pays": "Burundi", "capitale": "Gitega", "population": 12},
    {"continent": "Afrique", "pays": "Cabo Verde", "capitale": "Praia", "population": 0.56},
    {"continent": "Afrique", "pays": "Cameroun", "capitale": "Yaoundé", "population": 27},
    {"continent": "Afrique", "pays": "République centrafricaine", "capitale": "Bangui", "population": 4.7},
    {"continent": "Afrique", "pays": "Tchad", "capitale": "N'Djamena", "population": 16},
    {"continent": "Afrique", "pays": "Comores", "capitale": "Moroni", "population": 0.87},
    {"continent": "Afrique", "pays": "Congo (Brazzaville)", "capitale": "Brazzaville", "population": 5.5},
    {"continent": "Afrique", "pays": "Congo (Kinshasa)", "capitale": "Kinshasa", "population": 89},
    {"continent": "Afrique", "pays": "Côte d'Ivoire", "capitale": "Yamoussoukro", "population": 26},
    {"continent": "Afrique", "pays": "Djibouti", "capitale": "Djibouti", "population": 1},
    {"continent": "Afrique", "pays": "Égypte", "capitale": "Le Caire", "population": 104},
    {"continent": "Afrique", "pays": "Guinée équatoriale", "capitale": "Malabo", "population": 1.4},
    {"continent": "Afrique", "pays": "Érythrée", "capitale": "Asmara", "population": 3.6},
    {"continent": "Afrique", "pays": "Eswatini", "capitale": "Mbabane / Lobamba", "population": 1.2},
    {"continent": "Afrique", "pays": "Éthiopie", "capitale": "Addis-Abeba", "population": 115},
    {"continent": "Afrique", "pays": "Gabon", "capitale": "Libreville", "population": 2.2},
    {"continent": "Afrique", "pays": "Gambie", "capitale": "Banjul", "population": 2.4},
    {"continent": "Afrique", "pays": "Ghana", "capitale": "Accra", "population": 32},
    {"continent": "Afrique", "pays": "Guinée", "capitale": "Conakry", "population": 13},
    {"continent": "Afrique", "pays": "Guinée-Bissau", "capitale": "Bissau", "population": 1.9},
    {"continent": "Afrique", "pays": "Kenya", "capitale": "Nairobi", "population": 54},
    {"continent": "Afrique", "pays": "Lesotho", "capitale": "Maseru", "population": 2.1},
    {"continent": "Afrique", "pays": "Liberia", "capitale": "Monrovia", "population": 5},
    {"continent": "Afrique", "pays": "Libye", "capitale": "Tripoli", "population": 7},
    {"continent": "Afrique", "pays": "Madagascar", "capitale": "Antananarivo", "population": 28},
    {"continent": "Afrique", "pays": "Malawi", "capitale": "Lilongwe", "population": 19},
    {"continent": "Afrique", "pays": "Mali", "capitale": "Bamako", "population": 21},
    {"continent": "Afrique", "pays": "Mauritanie", "capitale": "Nouakchott", "population": 4.5},
    {"continent": "Afrique", "pays": "Maurice", "capitale": "Port-Louis", "population": 1.3},
    {"continent": "Afrique", "pays": "Maroc", "capitale": "Rabat", "population": 37},
    {"continent": "Afrique", "pays": "Mozambique", "capitale": "Maputo", "population": 31},
    {"continent": "Afrique", "pays": "Namibie", "capitale": "Windhoek", "population": 2.5},
    {"continent": "Afrique", "pays": "Niger", "capitale": "Niamey", "population": 24},
    {"continent": "Afrique", "pays": "Nigeria", "capitale": "Abuja", "population": 206},
    {"continent": "Afrique", "pays": "Rwanda", "capitale": "Kigali", "population": 13},
    {"continent": "Afrique", "pays": "Sao Tomé-et-Principe", "capitale": "São Tomé", "population": 0.22},
    {"continent": "Afrique", "pays": "Sénégal", "capitale": "Dakar", "population": 17},
    {"continent": "Afrique", "pays": "Seychelles", "capitale": "Victoria", "population": 0.1},
    {"continent": "Afrique", "pays": "Sierra Leone", "capitale": "Freetown", "population": 8},
    {"continent": "Afrique", "pays": "Somalie", "capitale": "Mogadiscio", "population": 16},
    {"continent": "Afrique", "pays": "Afrique du Sud", "capitale": "Pretoria / Cape Town", "population": 59},
    {"continent": "Afrique", "pays": "Soudan du Sud", "capitale": "Juba", "population": 11},
    {"continent": "Afrique", "pays": "Soudan", "capitale": "Khartoum", "population": 44},
    {"continent": "Afrique", "pays": "Tanzanie", "capitale": "Dodoma", "population": 61},
    {"continent": "Afrique", "pays": "Togo", "capitale": "Lomé", "population": 8},
    {"continent": "Afrique", "pays": "Tunisie", "capitale": "Tunis", "population": 12},
    {"continent": "Afrique", "pays": "Ouganda", "capitale": "Kampala", "population": 45},
    {"continent": "Afrique", "pays": "Zambie", "capitale": "Lusaka", "population": 18},
    {"continent": "Afrique", "pays": "Zimbabwe", "capitale": "Harare", "population": 15},

    # // Asie
    {"continent": "Asie", "pays": "Afghanistan", "capitale": "Kabul", "population": 38},
    {"continent": "Asie", "pays": "Arménie", "capitale": "Erevan", "population": 3},
    {"continent": "Asie", "pays": "Azerbaïdjan", "capitale": "Bakou", "population": 10},
    {"continent": "Asie", "pays": "Bahreïn", "capitale": "Manama", "population": 1.7},
    {"continent": "Asie", "pays": "Bangladesh", "capitale": "Dhaka", "population": 166},
    {"continent": "Asie", "pays": "Bhoutan", "capitale": "Thimphou", "population": 0.77},
    {"continent": "Asie", "pays": "Brunéi", "capitale": "Bandar Seri Begawan", "population": 0.44},
    {"continent": "Asie", "pays": "Cambodge", "capitale": "Phnom Penh", "population": 16},
    {"continent": "Asie", "pays": "Chine", "capitale": "Pékin", "population": 1402},
    {"continent": "Asie", "pays": "Chypre", "capitale": "Nicosie", "population": 1.2},
    {"continent": "Asie", "pays": "Géorgie", "capitale": "Tbilissi", "population": 3.7},
    {"continent": "Asie", "pays": "Inde", "capitale": "New Delhi", "population": 1380},
    {"continent": "Asie", "pays": "Indonésie", "capitale": "Jakarta", "population": 273},
    {"continent": "Asie", "pays": "Iran", "capitale": "Téhéran", "population": 85},
    {"continent": "Asie", "pays": "Iraq", "capitale": "Bagdad", "population": 43},
    {"continent": "Asie", "pays": "Israël", "capitale": "Jérusalem", "population": 9},
    {"continent": "Asie", "pays": "Japon", "capitale": "Tokyo", "population": 126},
    {"continent": "Asie", "pays": "Jordanie", "capitale": "Amman", "population": 10},
    {"continent": "Asie", "pays": "Kazakhstan", "capitale": "Noursoultan", "population": 19},
    {"continent": "Asie", "pays": "Koweït", "capitale": "Koweït", "population": 4.3},
    {"continent": "Asie", "pays": "Kirghizistan", "capitale": "Bichkek", "population": 6.5},
    {"continent": "Asie", "pays": "Laos", "capitale": "Vientiane", "population": 7},
    {"continent": "Asie", "pays": "Liban", "capitale": "Beyrouth", "population": 6.8},
    {"continent": "Asie", "pays": "Malaisie", "capitale": "Kuala Lumpur", "population": 32},
    {"continent": "Asie", "pays": "Maldives", "capitale": "Malé", "population": 0.5},
    {"continent": "Asie", "pays": "Mongolie", "capitale": "Oulan-Bator", "population": 3.3},
    {"continent": "Asie", "pays": "Myanmar", "capitale": "Naypyidaw", "population": 54},
    {"continent": "Asie", "pays": "Népal", "capitale": "Katmandou", "population": 29},
    {"continent": "Asie", "pays": "Corée du Nord", "capitale": "Pyongyang", "population": 25},
    {"continent": "Asie", "pays": "Oman", "capitale": "Mascate", "population": 5},
    {"continent": "Asie", "pays": "Pakistan", "capitale": "Islamabad", "population": 220},
    {"continent": "Asie", "pays": "Palestine", "capitale": "Ramallah / Jérusalem orientale", "population": 5},
    {"continent": "Asie", "pays": "Philippines", "capitale": "Manille", "population": 109},
    {"continent": "Asie", "pays": "Qatar", "capitale": "Doha", "population": 2.8},
    {"continent": "Asie", "pays": "Arabie Saoudite", "capitale": "Riyad", "population": 35},
    {"continent": "Asie", "pays": "Singapour", "capitale": "Singapour", "population": 5.7},
    {"continent": "Asie", "pays": "Corée du Sud", "capitale": "Séoul", "population": 51},
    {"continent": "Asie", "pays": "Sri Lanka", "capitale": "Sri Jayewardenepura Kotte", "population": 21},
    {"continent": "Asie", "pays": "Syrie", "capitale": "Damas", "population": 18},
    {"continent": "Asie", "pays": "Taïwan", "capitale": "Taipei", "population": 23},
    {"continent": "Asie", "pays": "Tadjikistan", "capitale": "Douchanbé", "population": 9.5},
    {"continent": "Asie", "pays": "Thaïlande", "capitale": "Bangkok", "population": 70},
    {"continent": "Asie", "pays": "Timor-Leste", "capitale": "Dili", "population": 1.3},
    {"continent": "Asie", "pays": "Turquie", "capitale": "Ankara", "population": 84},
    {"continent": "Asie", "pays": "Turkménistan", "capitale": "Achgabat", "population": 6},
    {"continent": "Asie", "pays": "Émirats arabes unis", "capitale": "Abou Dabi", "population": 10},
    {"continent": "Asie", "pays": "Ouzbékistan", "capitale": "Tachkent", "population": 34},
    {"continent": "Asie", "pays": "Vietnam", "capitale": "Hanoï", "population": 97},
    {"continent": "Asie", "pays": "Yémen", "capitale": "Sanaa", "population": 30},

    # // Europe
    {"continent": "Europe", "pays": "Albanie", "capitale": "Tirana", "population": 2.8},
    {"continent": "Europe", "pays": "Andorre", "capitale": "Andorre-la-Vieille", "population": 0.077},
    {"continent": "Europe", "pays": "Autriche", "capitale": "Vienne", "population": 9},
    {"continent": "Europe", "pays": "Biélorussie", "capitale": "Minsk", "population": 9.4},
    {"continent": "Europe", "pays": "Belgique", "capitale": "Bruxelles", "population": 11.5},
    {"continent": "Europe", "pays": "Bosnie-Herzégovine", "capitale": "Sarajevo", "population": 3.3},
    {"continent": "Europe", "pays": "Bulgarie", "capitale": "Sofia", "population": 7},
    {"continent": "Europe", "pays": "Croatie", "capitale": "Zagreb", "population": 4},
    {"continent": "Europe", "pays": "République tchèque", "capitale": "Prague", "population": 10.7},
    {"continent": "Europe", "pays": "Danemark", "capitale": "Copenhague", "population": 5.8},
    {"continent": "Europe", "pays": "Estonie", "capitale": "Tallinn", "population": 1.3},
    {"continent": "Europe", "pays": "Finlande", "capitale": "Helsinki", "population": 5.5},
    {"continent": "Europe", "pays": "France", "capitale": "Paris", "population": 68},
    {"continent": "Europe", "pays": "Allemagne", "capitale": "Berlin", "population": 83},
    {"continent": "Europe", "pays": "Grèce", "capitale": "Athènes", "population": 10.7},
    {"continent": "Europe", "pays": "Hongrie", "capitale": "Budapest", "population": 9.7},
    {"continent": "Europe", "pays": "Islande", "capitale": "Reykjavik", "population": 0.36},
    {"continent": "Europe", "pays": "Irlande", "capitale": "Dublin", "population": 5},
    {"continent": "Europe", "pays": "Italie", "capitale": "Rome", "population": 59},
    {"continent": "Europe", "pays": "Kosovo", "capitale": "Pristina", "population": 1.8},
    {"continent": "Europe", "pays": "Lettonie", "capitale": "Riga", "population": 1.9},
    {"continent": "Europe", "pays": "Liechtenstein", "capitale": "Vaduz", "population": 0.04},
    {"continent": "Europe", "pays": "Lituanie", "capitale": "Vilnius", "population": 2.8},
    {"continent": "Europe", "pays": "Luxembourg", "capitale": "Luxembourg", "population": 0.63},
    {"continent": "Europe", "pays": "Malte", "capitale": "La Valette", "population": 0.516},
    {"continent": "Europe", "pays": "Moldavie", "capitale": "Chisinau", "population": 2.7},
    {"continent": "Europe", "pays": "Monaco", "capitale": "Monaco", "population": 0.04},
    {"continent": "Europe", "pays": "Monténégro", "capitale": "Podgorica", "population": 0.62},
    {"continent": "Europe", "pays": "Pays-Bas", "capitale": "Amsterdam", "population": 17.5},
    {"continent": "Europe", "pays": "Macédoine du Nord", "capitale": "Skopje", "population": 2.1},
    {"continent": "Europe", "pays": "Norvège", "capitale": "Oslo", "population": 5.4},
    {"continent": "Europe", "pays": "Pologne", "capitale": "Varsovie", "population": 38},
    {"continent": "Europe", "pays": "Portugal", "capitale": "Lisbonne", "population": 10.3},
    {"continent": "Europe", "pays": "Roumanie", "capitale": "Bucarest", "population": 19},
    {"continent": "Europe", "pays": "Russie", "capitale": "Moscou", "population": 144},
    {"continent": "Europe", "pays": "Saint-Marin", "capitale": "Saint-Marin", "population": 0.034},
    {"continent": "Europe", "pays": "Serbie", "capitale": "Belgrade", "population": 7},
    {"continent": "Europe", "pays": "Slovaquie", "capitale": "Bratislava", "population": 5.5},
    {"continent": "Europe", "pays": "Slovénie", "capitale": "Ljubljana", "population": 2.1},
    {"continent": "Europe", "pays": "Espagne", "capitale": "Madrid", "population": 47},
    {"continent": "Europe", "pays": "Suède", "capitale": "Stockholm", "population": 10.4},
    {"continent": "Europe", "pays": "Suisse", "capitale": "Berne", "population": 8.6},
    {"continent": "Europe", "pays": "Ukraine", "capitale": "Kyiv", "population": 44},
    {"continent": "Europe", "pays": "Royaume-Uni", "capitale": "Londres", "population": 67},
    {"continent": "Europe", "pays": "Vatican", "capitale": "Cité du Vatican", "population": 0.001},

    # // Amérique
    {"continent": "Amérique", "pays": "Antigua-et-Barbuda", "capitale": "Saint John's", "population": 0.097},
    {"continent": "Amérique", "pays": "Bahamas", "capitale": "Nassau", "population": 0.39},
    {"continent": "Amérique", "pays": "Barbade", "capitale": "Bridgetown", "population": 0.287},
    {"continent": "Amérique", "pays": "Belize", "capitale": "Belmopan", "population": 0.39},
    {"continent": "Amérique", "pays": "Canada", "capitale": "Ottawa", "population": 38},
    {"continent": "Amérique", "pays": "Costa Rica", "capitale": "San José", "population": 5},
    {"continent": "Amérique", "pays": "Cuba", "capitale": "La Havane", "population": 11},
    {"continent": "Amérique", "pays": "Dominique", "capitale": "Roseau", "population": 0.072},
    {"continent": "Amérique", "pays": "République dominicaine", "capitale": "Saint-Domingue", "population": 10.8},
    {"continent": "Amérique", "pays": "El Salvador", "capitale": "San Salvador", "population": 6.5},
    {"continent": "Amérique", "pays": "Grenade", "capitale": "Saint-Georges", "population": 0.11},
    {"continent": "Amérique", "pays": "Guatemala", "capitale": "Guatemala", "population": 18},
    {"continent": "Amérique", "pays": "Haïti", "capitale": "Port-au-Prince", "population": 11.4},
    {"continent": "Amérique", "pays": "Honduras", "capitale": "Tegucigalpa", "population": 9.9},
    {"continent": "Amérique", "pays": "Jamaïque", "capitale": "Kingston", "population": 2.9},
    {"continent": "Amérique", "pays": "Mexique", "capitale": "Mexico", "population": 126},
    {"continent": "Amérique", "pays": "Nicaragua", "capitale": "Managua", "population": 6.8},
    {"continent": "Amérique", "pays": "Panama", "capitale": "Panama", "population": 4.4},
    {"continent": "Amérique", "pays": "Saint-Kitts-et-Nevis", "capitale": "Basseterre", "population": 0.053},
    {"continent": "Amérique", "pays": "Sainte-Lucie", "capitale": "Castries", "population": 0.183},
    {"continent": "Amérique", "pays": "Saint-Vincent-et-les Grenadines", "capitale": "Kingstown", "population": 0.11},
    {"continent": "Amérique", "pays": "Trinité-et-Tobago", "capitale": "Port-d'Espagne", "population": 1.4},
    {"continent": "Amérique", "pays": "États-Unis", "capitale": "Washington", "population": 331},
    {"continent": "Amérique", "pays": "Argentine", "capitale": "Buenos Aires", "population": 45},
    {"continent": "Amérique", "pays": "Bolivie", "capitale": "Sucre / La Paz", "population": 11},
    {"continent": "Amérique", "pays": "Brésil", "capitale": "Brasilia", "population": 214},
    {"continent": "Amérique", "pays": "Chili", "capitale": "Santiago", "population": 19},
    {"continent": "Amérique", "pays": "Colombie", "capitale": "Bogota", "population": 50},
    {"continent": "Amérique", "pays": "Équateur", "capitale": "Quito", "population": 17.6},
    {"continent": "Amérique", "pays": "Guyana", "capitale": "Georgetown", "population": 0.79},
    {"continent": "Amérique", "pays": "Paraguay", "capitale": "Asuncion", "population": 7},
    {"continent": "Amérique", "pays": "Pérou", "capitale": "Lima", "population": 33},
    {"continent": "Amérique", "pays": "Suriname", "capitale": "Paramaribo", "population": 0.59},
    {"continent": "Amérique", "pays": "Uruguay", "capitale": "Montevideo", "population": 3.5},
    {"continent": "Amérique", "pays": "Venezuela", "capitale": "Caracas", "population": 28},

    # // Océanie
    {"continent": "Océanie", "pays": "Australie", "capitale": "Canberra", "population": 26},
    {"continent": "Océanie", "pays": "Fidji", "capitale": "Suva", "population": 0.9},
    {"continent": "Océanie", "pays": "Kiribati", "capitale": "Tarawa", "population": 0.12},
    {"continent": "Océanie", "pays": "Îles Marshall", "capitale": "Majuro", "population": 0.06},
    {"continent": "Océanie", "pays": "Micronésie", "capitale": "Palikir", "population": 0.11},
    {"continent": "Océanie", "pays": "Nauru", "capitale": "Yaren", "population": 0.01},
    {"continent": "Océanie", "pays": "Nouvelle-Zélande", "capitale": "Wellington", "population": 5},
    {"continent": "Océanie", "pays": "Palaos", "capitale": "Ngerulmud", "population": 0.018},
    {"continent": "Océanie", "pays": "Papouasie-Nouvelle-Guinée", "capitale": "Port Moresby", "population": 9},
    {"continent": "Océanie", "pays": "Samoa", "capitale": "Apia", "population": 0.2},
    {"continent": "Océanie", "pays": "Îles Salomon", "capitale": "Honiara", "population": 0.7},
    {"continent": "Océanie", "pays": "Tonga", "capitale": "Nuku'alofa", "population": 0.1},
    {"continent": "Océanie", "pays": "Tuvalu", "capitale": "Funafuti", "population": 0.011},
    {"continent": "Océanie", "pays": "Vanuatu", "capitale": "Port-Vila", "population": 0.3}
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
        [KeyboardButton("capitale → Pays"), KeyboardButton("Pays → capitale")],
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
        "📚 <b>Aide du Bot Pays & capitales</b>\n\n"
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
        
    elif user_text in ["Pays → capitale", "capitale → Pays"]:
        user_data['question_type'] = 'pays_capitale' if user_text == "Pays → capitale" else 'capitale_pays'
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
        feedback = f"✅ <b>Correct !</b>"
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
    
    for pays in COUNTRIES_DATA:
        if (search_term in pays['pays'].lower() or 
            search_term in pays['capitale'].lower() or
            search_term in pays['continent'].lower()):
            results.append(pays)
    
    if results:
        message = "🔎 <b>Résultats de recherche :</b>\n\n"
        for result in results:
            message += (
                f"🏴 <b>{result['pays']}</b>\n"
                f"🏛️ capitale : {result['capitale']}\n"
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