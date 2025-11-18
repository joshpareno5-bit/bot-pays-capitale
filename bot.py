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
[
    # // Afrique
    {"continent": "Afrique", "country": "Algérie", "capital": "Alger", "population": 43},
    {"continent": "Afrique", "country": "Angola", "capital": "Luanda", "population": 33},
    {"continent": "Afrique", "country": "Bénin", "capital": "Porto-Novo", "population": 12},
    {"continent": "Afrique", "country": "Botswana", "capital": "Gaborone", "population": 2.4},
    {"continent": "Afrique", "country": "Burkina Faso", "capital": "Ouagadougou", "population": 21},
    {"continent": "Afrique", "country": "Burundi", "capital": "Gitega", "population": 12},
    {"continent": "Afrique", "country": "Cabo Verde", "capital": "Praia", "population": 0.56},
    {"continent": "Afrique", "country": "Cameroun", "capital": "Yaoundé", "population": 27},
    {"continent": "Afrique", "country": "République centrafricaine", "capital": "Bangui", "population": 4.7},
    {"continent": "Afrique", "country": "Tchad", "capital": "N'Djamena", "population": 16},
    {"continent": "Afrique", "country": "Comores", "capital": "Moroni", "population": 0.87},
    {"continent": "Afrique", "country": "Congo (Brazzaville)", "capital": "Brazzaville", "population": 5.5},
    {"continent": "Afrique", "country": "Congo (Kinshasa)", "capital": "Kinshasa", "population": 89},
    {"continent": "Afrique", "country": "Côte d'Ivoire", "capital": "Yamoussoukro", "population": 26},
    {"continent": "Afrique", "country": "Djibouti", "capital": "Djibouti", "population": 1},
    {"continent": "Afrique", "country": "Égypte", "capital": "Le Caire", "population": 104},
    {"continent": "Afrique", "country": "Guinée équatoriale", "capital": "Malabo", "population": 1.4},
    {"continent": "Afrique", "country": "Érythrée", "capital": "Asmara", "population": 3.6},
    {"continent": "Afrique", "country": "Eswatini", "capital": "Mbabane / Lobamba", "population": 1.2},
    {"continent": "Afrique", "country": "Éthiopie", "capital": "Addis-Abeba", "population": 115},
    {"continent": "Afrique", "country": "Gabon", "capital": "Libreville", "population": 2.2},
    {"continent": "Afrique", "country": "Gambie", "capital": "Banjul", "population": 2.4},
    {"continent": "Afrique", "country": "Ghana", "capital": "Accra", "population": 32},
    {"continent": "Afrique", "country": "Guinée", "capital": "Conakry", "population": 13},
    {"continent": "Afrique", "country": "Guinée-Bissau", "capital": "Bissau", "population": 1.9},
    {"continent": "Afrique", "country": "Kenya", "capital": "Nairobi", "population": 54},
    {"continent": "Afrique", "country": "Lesotho", "capital": "Maseru", "population": 2.1},
    {"continent": "Afrique", "country": "Liberia", "capital": "Monrovia", "population": 5},
    {"continent": "Afrique", "country": "Libye", "capital": "Tripoli", "population": 7},
    {"continent": "Afrique", "country": "Madagascar", "capital": "Antananarivo", "population": 28},
    {"continent": "Afrique", "country": "Malawi", "capital": "Lilongwe", "population": 19},
    {"continent": "Afrique", "country": "Mali", "capital": "Bamako", "population": 21},
    {"continent": "Afrique", "country": "Mauritanie", "capital": "Nouakchott", "population": 4.5},
    {"continent": "Afrique", "country": "Maurice", "capital": "Port-Louis", "population": 1.3},
    {"continent": "Afrique", "country": "Maroc", "capital": "Rabat", "population": 37},
    {"continent": "Afrique", "country": "Mozambique", "capital": "Maputo", "population": 31},
    {"continent": "Afrique", "country": "Namibie", "capital": "Windhoek", "population": 2.5},
    {"continent": "Afrique", "country": "Niger", "capital": "Niamey", "population": 24},
    {"continent": "Afrique", "country": "Nigeria", "capital": "Abuja", "population": 206},
    {"continent": "Afrique", "country": "Rwanda", "capital": "Kigali", "population": 13},
    {"continent": "Afrique", "country": "Sao Tomé-et-Principe", "capital": "São Tomé", "population": 0.22},
    {"continent": "Afrique", "country": "Sénégal", "capital": "Dakar", "population": 17},
    {"continent": "Afrique", "country": "Seychelles", "capital": "Victoria", "population": 0.1},
    {"continent": "Afrique", "country": "Sierra Leone", "capital": "Freetown", "population": 8},
    {"continent": "Afrique", "country": "Somalie", "capital": "Mogadiscio", "population": 16},
    {"continent": "Afrique", "country": "Afrique du Sud", "capital": "Pretoria / Cape Town", "population": 59},
    {"continent": "Afrique", "country": "Soudan du Sud", "capital": "Juba", "population": 11},
    {"continent": "Afrique", "country": "Soudan", "capital": "Khartoum", "population": 44},
    {"continent": "Afrique", "country": "Tanzanie", "capital": "Dodoma", "population": 61},
    {"continent": "Afrique", "country": "Togo", "capital": "Lomé", "population": 8},
    {"continent": "Afrique", "country": "Tunisie", "capital": "Tunis", "population": 12},
    {"continent": "Afrique", "country": "Ouganda", "capital": "Kampala", "population": 45},
    {"continent": "Afrique", "country": "Zambie", "capital": "Lusaka", "population": 18},
    {"continent": "Afrique", "country": "Zimbabwe", "capital": "Harare", "population": 15},

    # // Asie
    {"continent": "Asie", "country": "Afghanistan", "capital": "Kabul", "population": 38},
    {"continent": "Asie", "country": "Arménie", "capital": "Erevan", "population": 3},
    {"continent": "Asie", "country": "Azerbaïdjan", "capital": "Bakou", "population": 10},
    {"continent": "Asie", "country": "Bahreïn", "capital": "Manama", "population": 1.7},
    {"continent": "Asie", "country": "Bangladesh", "capital": "Dhaka", "population": 166},
    {"continent": "Asie", "country": "Bhoutan", "capital": "Thimphou", "population": 0.77},
    {"continent": "Asie", "country": "Brunéi", "capital": "Bandar Seri Begawan", "population": 0.44},
    {"continent": "Asie", "country": "Cambodge", "capital": "Phnom Penh", "population": 16},
    {"continent": "Asie", "country": "Chine", "capital": "Pékin", "population": 1402},
    {"continent": "Asie", "country": "Chypre", "capital": "Nicosie", "population": 1.2},
    {"continent": "Asie", "country": "Géorgie", "capital": "Tbilissi", "population": 3.7},
    {"continent": "Asie", "country": "Inde", "capital": "New Delhi", "population": 1380},
    {"continent": "Asie", "country": "Indonésie", "capital": "Jakarta", "population": 273},
    {"continent": "Asie", "country": "Iran", "capital": "Téhéran", "population": 85},
    {"continent": "Asie", "country": "Iraq", "capital": "Bagdad", "population": 43},
    {"continent": "Asie", "country": "Israël", "capital": "Jérusalem", "population": 9},
    {"continent": "Asie", "country": "Japon", "capital": "Tokyo", "population": 126},
    {"continent": "Asie", "country": "Jordanie", "capital": "Amman", "population": 10},
    {"continent": "Asie", "country": "Kazakhstan", "capital": "Noursoultan", "population": 19},
    {"continent": "Asie", "country": "Koweït", "capital": "Koweït", "population": 4.3},
    {"continent": "Asie", "country": "Kirghizistan", "capital": "Bichkek", "population": 6.5},
    {"continent": "Asie", "country": "Laos", "capital": "Vientiane", "population": 7},
    {"continent": "Asie", "country": "Liban", "capital": "Beyrouth", "population": 6.8},
    {"continent": "Asie", "country": "Malaisie", "capital": "Kuala Lumpur", "population": 32},
    {"continent": "Asie", "country": "Maldives", "capital": "Malé", "population": 0.5},
    {"continent": "Asie", "country": "Mongolie", "capital": "Oulan-Bator", "population": 3.3},
    {"continent": "Asie", "country": "Myanmar", "capital": "Naypyidaw", "population": 54},
    {"continent": "Asie", "country": "Népal", "capital": "Katmandou", "population": 29},
    {"continent": "Asie", "country": "Corée du Nord", "capital": "Pyongyang", "population": 25},
    {"continent": "Asie", "country": "Oman", "capital": "Mascate", "population": 5},
    {"continent": "Asie", "country": "Pakistan", "capital": "Islamabad", "population": 220},
    {"continent": "Asie", "country": "Palestine", "capital": "Ramallah / Jérusalem orientale", "population": 5},
    {"continent": "Asie", "country": "Philippines", "capital": "Manille", "population": 109},
    {"continent": "Asie", "country": "Qatar", "capital": "Doha", "population": 2.8},
    {"continent": "Asie", "country": "Arabie Saoudite", "capital": "Riyad", "population": 35},
    {"continent": "Asie", "country": "Singapour", "capital": "Singapour", "population": 5.7},
    {"continent": "Asie", "country": "Corée du Sud", "capital": "Séoul", "population": 51},
    {"continent": "Asie", "country": "Sri Lanka", "capital": "Sri Jayewardenepura Kotte", "population": 21},
    {"continent": "Asie", "country": "Syrie", "capital": "Damas", "population": 18},
    {"continent": "Asie", "country": "Taïwan", "capital": "Taipei", "population": 23},
    {"continent": "Asie", "country": "Tadjikistan", "capital": "Douchanbé", "population": 9.5},
    {"continent": "Asie", "country": "Thaïlande", "capital": "Bangkok", "population": 70},
    {"continent": "Asie", "country": "Timor-Leste", "capital": "Dili", "population": 1.3},
    {"continent": "Asie", "country": "Turquie", "capital": "Ankara", "population": 84},
    {"continent": "Asie", "country": "Turkménistan", "capital": "Achgabat", "population": 6},
    {"continent": "Asie", "country": "Émirats arabes unis", "capital": "Abou Dabi", "population": 10},
    {"continent": "Asie", "country": "Ouzbékistan", "capital": "Tachkent", "population": 34},
    {"continent": "Asie", "country": "Vietnam", "capital": "Hanoï", "population": 97},
    {"continent": "Asie", "country": "Yémen", "capital": "Sanaa", "population": 30},

    # // Europe
    {"continent": "Europe", "country": "Albanie", "capital": "Tirana", "population": 2.8},
    {"continent": "Europe", "country": "Andorre", "capital": "Andorre-la-Vieille", "population": 0.077},
    {"continent": "Europe", "country": "Autriche", "capital": "Vienne", "population": 9},
    {"continent": "Europe", "country": "Biélorussie", "capital": "Minsk", "population": 9.4},
    {"continent": "Europe", "country": "Belgique", "capital": "Bruxelles", "population": 11.5},
    {"continent": "Europe", "country": "Bosnie-Herzégovine", "capital": "Sarajevo", "population": 3.3},
    {"continent": "Europe", "country": "Bulgarie", "capital": "Sofia", "population": 7},
    {"continent": "Europe", "country": "Croatie", "capital": "Zagreb", "population": 4},
    {"continent": "Europe", "country": "République tchèque", "capital": "Prague", "population": 10.7},
    {"continent": "Europe", "country": "Danemark", "capital": "Copenhague", "population": 5.8},
    {"continent": "Europe", "country": "Estonie", "capital": "Tallinn", "population": 1.3},
    {"continent": "Europe", "country": "Finlande", "capital": "Helsinki", "population": 5.5},
    {"continent": "Europe", "country": "France", "capital": "Paris", "population": 68},
    {"continent": "Europe", "country": "Allemagne", "capital": "Berlin", "population": 83},
    {"continent": "Europe", "country": "Grèce", "capital": "Athènes", "population": 10.7},
    {"continent": "Europe", "country": "Hongrie", "capital": "Budapest", "population": 9.7},
    {"continent": "Europe", "country": "Islande", "capital": "Reykjavik", "population": 0.36},
    {"continent": "Europe", "country": "Irlande", "capital": "Dublin", "population": 5},
    {"continent": "Europe", "country": "Italie", "capital": "Rome", "population": 59},
    {"continent": "Europe", "country": "Kosovo", "capital": "Pristina", "population": 1.8},
    {"continent": "Europe", "country": "Lettonie", "capital": "Riga", "population": 1.9},
    {"continent": "Europe", "country": "Liechtenstein", "capital": "Vaduz", "population": 0.04},
    {"continent": "Europe", "country": "Lituanie", "capital": "Vilnius", "population": 2.8},
    {"continent": "Europe", "country": "Luxembourg", "capital": "Luxembourg", "population": 0.63},
    {"continent": "Europe", "country": "Malte", "capital": "La Valette", "population": 0.516},
    {"continent": "Europe", "country": "Moldavie", "capital": "Chisinau", "population": 2.7},
    {"continent": "Europe", "country": "Monaco", "capital": "Monaco", "population": 0.04},
    {"continent": "Europe", "country": "Monténégro", "capital": "Podgorica", "population": 0.62},
    {"continent": "Europe", "country": "Pays-Bas", "capital": "Amsterdam", "population": 17.5},
    {"continent": "Europe", "country": "Macédoine du Nord", "capital": "Skopje", "population": 2.1},
    {"continent": "Europe", "country": "Norvège", "capital": "Oslo", "population": 5.4},
    {"continent": "Europe", "country": "Pologne", "capital": "Varsovie", "population": 38},
    {"continent": "Europe", "country": "Portugal", "capital": "Lisbonne", "population": 10.3},
    {"continent": "Europe", "country": "Roumanie", "capital": "Bucarest", "population": 19},
    {"continent": "Europe", "country": "Russie", "capital": "Moscou", "population": 144},
    {"continent": "Europe", "country": "Saint-Marin", "capital": "Saint-Marin", "population": 0.034},
    {"continent": "Europe", "country": "Serbie", "capital": "Belgrade", "population": 7},
    {"continent": "Europe", "country": "Slovaquie", "capital": "Bratislava", "population": 5.5},
    {"continent": "Europe", "country": "Slovénie", "capital": "Ljubljana", "population": 2.1},
    {"continent": "Europe", "country": "Espagne", "capital": "Madrid", "population": 47},
    {"continent": "Europe", "country": "Suède", "capital": "Stockholm", "population": 10.4},
    {"continent": "Europe", "country": "Suisse", "capital": "Berne", "population": 8.6},
    {"continent": "Europe", "country": "Ukraine", "capital": "Kyiv", "population": 44},
    {"continent": "Europe", "country": "Royaume-Uni", "capital": "Londres", "population": 67},
    {"continent": "Europe", "country": "Vatican", "capital": "Cité du Vatican", "population": 0.001},

    # // Amérique
    {"continent": "Amérique", "country": "Antigua-et-Barbuda", "capital": "Saint John's", "population": 0.097},
    {"continent": "Amérique", "country": "Bahamas", "capital": "Nassau", "population": 0.39},
    {"continent": "Amérique", "country": "Barbade", "capital": "Bridgetown", "population": 0.287},
    {"continent": "Amérique", "country": "Belize", "capital": "Belmopan", "population": 0.39},
    {"continent": "Amérique", "country": "Canada", "capital": "Ottawa", "population": 38},
    {"continent": "Amérique", "country": "Costa Rica", "capital": "San José", "population": 5},
    {"continent": "Amérique", "country": "Cuba", "capital": "La Havane", "population": 11},
    {"continent": "Amérique", "country": "Dominique", "capital": "Roseau", "population": 0.072},
    {"continent": "Amérique", "country": "République dominicaine", "capital": "Saint-Domingue", "population": 10.8},
    {"continent": "Amérique", "country": "El Salvador", "capital": "San Salvador", "population": 6.5},
    {"continent": "Amérique", "country": "Grenade", "capital": "Saint-Georges", "population": 0.11},
    {"continent": "Amérique", "country": "Guatemala", "capital": "Guatemala", "population": 18},
    {"continent": "Amérique", "country": "Haïti", "capital": "Port-au-Prince", "population": 11.4},
    {"continent": "Amérique", "country": "Honduras", "capital": "Tegucigalpa", "population": 9.9},
    {"continent": "Amérique", "country": "Jamaïque", "capital": "Kingston", "population": 2.9},
    {"continent": "Amérique", "country": "Mexique", "capital": "Mexico", "population": 126},
    {"continent": "Amérique", "country": "Nicaragua", "capital": "Managua", "population": 6.8},
    {"continent": "Amérique", "country": "Panama", "capital": "Panama", "population": 4.4},
    {"continent": "Amérique", "country": "Saint-Kitts-et-Nevis", "capital": "Basseterre", "population": 0.053},
    {"continent": "Amérique", "country": "Sainte-Lucie", "capital": "Castries", "population": 0.183},
    {"continent": "Amérique", "country": "Saint-Vincent-et-les Grenadines", "capital": "Kingstown", "population": 0.11},
    {"continent": "Amérique", "country": "Trinité-et-Tobago", "capital": "Port-d'Espagne", "population": 1.4},
    {"continent": "Amérique", "country": "États-Unis", "capital": "Washington", "population": 331},
    {"continent": "Amérique", "country": "Argentine", "capital": "Buenos Aires", "population": 45},
    {"continent": "Amérique", "country": "Bolivie", "capital": "Sucre / La Paz", "population": 11},
    {"continent": "Amérique", "country": "Brésil", "capital": "Brasilia", "population": 214},
    {"continent": "Amérique", "country": "Chili", "capital": "Santiago", "population": 19},
    {"continent": "Amérique", "country": "Colombie", "capital": "Bogota", "population": 50},
    {"continent": "Amérique", "country": "Équateur", "capital": "Quito", "population": 17.6},
    {"continent": "Amérique", "country": "Guyana", "capital": "Georgetown", "population": 0.79},
    {"continent": "Amérique", "country": "Paraguay", "capital": "Asuncion", "population": 7},
    {"continent": "Amérique", "country": "Pérou", "capital": "Lima", "population": 33},
    {"continent": "Amérique", "country": "Suriname", "capital": "Paramaribo", "population": 0.59},
    {"continent": "Amérique", "country": "Uruguay", "capital": "Montevideo", "population": 3.5},
    {"continent": "Amérique", "country": "Venezuela", "capital": "Caracas", "population": 28},

    # // Océanie
    {"continent": "Océanie", "country": "Australie", "capital": "Canberra", "population": 26},
    {"continent": "Océanie", "country": "Fidji", "capital": "Suva", "population": 0.9},
    {"continent": "Océanie", "country": "Kiribati", "capital": "Tarawa", "population": 0.12},
    {"continent": "Océanie", "country": "Îles Marshall", "capital": "Majuro", "population": 0.06},
    {"continent": "Océanie", "country": "Micronésie", "capital": "Palikir", "population": 0.11},
    {"continent": "Océanie", "country": "Nauru", "capital": "Yaren", "population": 0.01},
    {"continent": "Océanie", "country": "Nouvelle-Zélande", "capital": "Wellington", "population": 5},
    {"continent": "Océanie", "country": "Palaos", "capital": "Ngerulmud", "population": 0.018},
    {"continent": "Océanie", "country": "Papouasie-Nouvelle-Guinée", "capital": "Port Moresby", "population": 9},
    {"continent": "Océanie", "country": "Samoa", "capital": "Apia", "population": 0.2},
    {"continent": "Océanie", "country": "Îles Salomon", "capital": "Honiara", "population": 0.7},
    {"continent": "Océanie", "country": "Tonga", "capital": "Nuku'alofa", "population": 0.1},
    {"continent": "Océanie", "country": "Tuvalu", "capital": "Funafuti", "population": 0.011},
    {"continent": "Océanie", "country": "Vanuatu", "capital": "Port-Vila", "population": 0.3}
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