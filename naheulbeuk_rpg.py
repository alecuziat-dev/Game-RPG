import tkinter as tk
import random
import os
from PIL import Image, ImageTk

# --- JEU : LE DONJON DE NAHEULBEUK ---
# Interface graphique Tkinter pour un mini-RPG textuel.

# Dossier du script pour retrouver les images
# Si __file__ n'existe pas selon l'environnement, on prend le dossier courant
if "__file__" in globals():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    SCRIPT_DIR = os.getcwd()

# Compatibilité Pillow selon la version installée
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

# --- VARIABLES GLOBALES ---
hero = None
current_monster = None
current_room = 0
image_display_label = None
victory_image_ref = None
gameover_image_ref = None

ROOMS_BEFORE_BOSS = 20

selected_gender = "Aléatoire"
selected_race = "Aléatoire"
selected_class = "Aléatoire"

# --- DONNÉES DE BASE ---
races = ["Humain", "Ogre", "Elfe", "Thérianthropes", "Nain", "Elfe noir", "Mort vivant", "Orc"]

classes_data = {
    "Guerrier": {
        "bonus": "force", "valeur": 4,
        "sort1": "Coup de Bouclier", "cout1": 10,
        "sort2": "Exécution", "cout2": 20,
        "arme": {"nom": "Épée en fer blanc", "rare": "Commun", "dmg": 4, "stat": "force", "stat_val": 0}
    },
    "Évêque": {
        "bonus": "intelligence", "valeur": 4,
        "sort1": "Soins Mineurs", "cout1": 10,
        "sort2": "Colère Divine", "cout2": 20,
        "arme": {"nom": "Croix en bois lourd", "rare": "Commun", "dmg": 2, "stat": "intelligence", "stat_val": 1}
    },
    "Mage": {
        "bonus": "intelligence", "valeur": 4,
        "sort1": "Boule de Feu", "cout1": 12,
        "sort2": "Éclair Enchaîné", "cout2": 22,
        "arme": {"nom": "Bâton tordu", "rare": "Commun", "dmg": 2, "stat": "intelligence", "stat_val": 2}
    },
    "Assassin": {
        "bonus": "adresse", "valeur": 4,
        "sort1": "Attaque Sournoise", "cout1": 8,
        "sort2": "Lame Toxique", "cout2": 15,
        "arme": {"nom": "Dague émoussée", "rare": "Commun", "dmg": 3, "stat": "adresse", "stat_val": 1}
    },
    "Paladin": {
        "bonus": "courage", "valeur": 4,
        "sort1": "Justice Divine", "cout1": 10,
        "sort2": "Bouclier Lumineux", "cout2": 20,
        "arme": {"nom": "Marteau bénit", "rare": "Commun", "dmg": 4, "stat": "courage", "stat_val": 1}
    },
    "Ranger": {
        "bonus": "adresse", "valeur": 4,
        "sort1": "Tir Précis", "cout1": 8,
        "sort2": "Pluie de Flèches", "cout2": 18,
        "arme": {"nom": "Arc bancal", "rare": "Commun", "dmg": 3, "stat": "adresse", "stat_val": 2}
    },
    "Barde": {
        "bonus": "tous", "valeur": 1,
        "sort1": "Esprit Totem", "cout1": 10,
        "sort2": "Flûte Insupportable", "cout2": 18,
        "arme": {"nom": "Luth fissuré", "rare": "Commun", "dmg": 2, "stat": "courage", "stat_val": 1}
    }
}

classes = list(classes_data.keys())

male_first_names = ["Roger", "Glandulf", "Ulrik", "Borg", "Gérard", "Hubert", "Théobald", "Krom"]
female_first_names = ["Mélusine", "Gertrude", "Hildegarde", "Yvette", "Maëlys", "Brunehilde", "Sigrid", "Bertille"]

male_titles = ["le Malpropre", "le Fourbe", "le Bagarreur", "l'Égaré", "le Vaillant", "le Malchanceux"]
female_titles = ["la Cruelle", "la Rancunière", "la Brute", "l'Égarée", "la Vaillante", "la Malchanceuse"]

particularities = [
    "A peur des canards",
    "Déteste les escaliers",
    "Parle aux cailloux",
    "Collectionne les chaussettes trouées",
    "Se gratte en pleine baston",
    "Récite des poèmes nuls",
    "Sent la cave humide",
    "Jure en ancien elfique"
]

phrases_left = [
    "Porte de gauche douteuse",
    "Couloir sombre à gauche",
    "Passage avec courant d'air",
    "Une porte qui grince"
]
phrases_middle = [
    "Grande porte au centre",
    "Passage principal",
    "Couloir décoré bizarrement",
    "Une arche suspecte"
]
phrases_right = [
    "Petite porte de droite",
    "Passage étroit",
    "Couloir qui sent mauvais",
    "Entrée peu rassurante"
]

prefix_weapons = ["Épée", "Hache", "Bâton", "Dague", "Marteau", "Arc", "Lance"]
suffix_common = ["de travers", "moisi", "cabossé", "du pauvre", "rouillé"]
suffix_rare = ["du sanglier noir", "des collines", "des ombres", "de l'aube", "de guerre"]
suffix_legendary = ["de Gladeulfeurha", "du destin absurde", "des Anciens Donjons", "du chaos mou", "du maître perdu"]

monsters_pool = [
    {"nom": "Gobelin myope", "force": 8, "pv": 18, "xp": 25},
    {"nom": "Orc enrhumé", "force": 10, "pv": 24, "xp": 35},
    {"nom": "Squelette grinçant", "force": 9, "pv": 22, "xp": 30},
    {"nom": "Bandit fatigué", "force": 11, "pv": 26, "xp": 40},
    {"nom": "Zombie administratif", "force": 12, "pv": 30, "xp": 45}
]

# --- FONCTIONS UTILITAIRES ---

def load_game_image(filename, size=(650, 320)):
    # Charge une image depuis le dossier du script
    # Retourne une PhotoImage si tout va bien, sinon None
    img_path = os.path.join(SCRIPT_DIR, filename)

    if not os.path.exists(img_path):
        print(f"Image introuvable : {img_path}")
        return None

    try:
        pil_img = Image.open(img_path)
        pil_img = pil_img.resize(size, RESAMPLE)
        return ImageTk.PhotoImage(pil_img)
    except Exception as e:
        print(f"Erreur lors du chargement de {img_path} : {e}")
        return None


def show_end_image(img_ref):
    # Affiche une image de fin de partie
    global image_display_label

    if img_ref is None:
        return False

    if image_display_label is not None:
        image_display_label.destroy()
        image_display_label = None

    image_display_label = tk.Label(window, image=img_ref, bg="#2d1b0f")
    image_display_label.pack(pady=10)
    return True


def choose_gender(gender, clicked_btn):
    # Sélection du genre
    global selected_gender
    selected_gender = gender
    for b in frame_genre.winfo_children():
        b.config(bg="#f0f0f0", fg="black")
    clicked_btn.config(bg="gold", fg="black")


def choose_race(race, clicked_btn):
    # Sélection de la race
    global selected_race
    selected_race = race
    for b in frame_race.winfo_children():
        b.config(bg="#f0f0f0", fg="black")
    clicked_btn.config(bg="#32cd32", fg="white")


def choose_class(char_class, clicked_btn):
    # Sélection de la classe
    global selected_class
    selected_class = char_class
    for b in frame_classe.winfo_children():
        b.config(bg="#f0f0f0", fg="black")
    clicked_btn.config(bg="#32cd32", fg="white")


# --- SYSTÈME DE JEU ---

def generate_character():
    # Génère un nouveau héros et démarre la partie
    global hero, current_room, image_display_label, current_monster

    current_room = 0
    current_monster = None
    entered_name = entree_nom.get().strip()

    if image_display_label is not None:
        image_display_label.destroy()
        image_display_label = None

    gender = random.choice(["homme", "femme"]) if selected_gender == "Aléatoire" else selected_gender

    if entered_name == "":
        first_name = random.choice(male_first_names if gender == "homme" else female_first_names)
        title = random.choice(male_titles if gender == "homme" else female_titles)
        name = f"{first_name} {title}"
    else:
        name = entered_name

    race = random.choice(races) if selected_race == "Aléatoire" else selected_race
    char_class = random.choice(classes) if selected_class == "Aléatoire" else selected_class

    class_info = classes_data[char_class]

    strength = random.randint(8, 16) + (class_info["valeur"] if class_info["bonus"] in ["force", "tous"] else 0)
    intelligence = random.randint(8, 16) + (class_info["valeur"] if class_info["bonus"] in ["intelligence", "tous"] else 0)
    dexterity = random.randint(8, 16) + (class_info["valeur"] if class_info["bonus"] in ["adresse", "tous"] else 0)
    courage = random.randint(8, 16) + (class_info["valeur"] if class_info["bonus"] in ["courage", "tous"] else 0)

    hero = {
        "nom": name,
        "genre": gender,
        "race": race,
        "classe": char_class,
        "courage": courage,
        "intelligence": intelligence,
        "force": strength,
        "adresse": dexterity,
        "pv": 50,
        "pv_max": 50,
        "mana": 30,
        "mana_max": 30,
        "niveau": 1,
        "xp": 0,
        "xp_requis": 100,
        "or": 20,
        "particularites": random.sample(particularities, 2),
        "arme": class_info["arme"].copy(),
        "loot_weapon": None
    }

    frame_menu_creation.pack_forget()
    status_label.pack(fill="x", padx=40, pady=5)
    refresh_hero_display()

    class_info = classes_data[hero["classe"]]
    skill1_btn.config(text=f"✨ {class_info['sort1']} ({class_info['cout1']} PM)")
    skill2_btn.config(text=f"🔒 {class_info['sort2']} (Niv 2)", state="disabled", bg="grey")

    log_feed.config(text=f"{hero['nom']} entre dans le donjon. Mauvaise idée, excellent divertissement.", fg="white")
    generate_path_choices()


def refresh_hero_display():
    # Met à jour la fiche du héros
    if hero is None:
        return

    f_b = hero["arme"]["stat_val"] if hero["arme"]["stat"] == "force" else 0
    i_b = hero["arme"]["stat_val"] if hero["arme"]["stat"] == "intelligence" else 0
    a_b = hero["arme"]["stat_val"] if hero["arme"]["stat"] == "adresse" else 0
    c_b = hero["arme"]["stat_val"] if hero["arme"]["stat"] == "courage" else 0

    rarity_tag = f"[{hero['arme']['rare']}]"

    text_data = f"""📇 FICHE D'AVENTURIER (Niveau {hero['niveau']}) | 🏰 Salle : {current_room}/{ROOMS_BEFORE_BOSS} 📇
Nom : {hero['nom']} ({hero['genre']}) - {hero['race']} {hero['classe']}
❤️ PV : {hero['pv']}/{hero['pv_max']}      🧪 MANA : {hero['mana']}/{hero['mana_max']}      ✨ XP : {hero['xp']}/{hero['xp_requis']}      🪙 OR : {hero['or']} pièces

⚔ Courage : {hero['courage'] + c_b} ({hero['courage']}+{c_b})   🧠 Intelligence : {hero['intelligence'] + i_b} ({hero['intelligence']}+{i_b})
💪 Force : {hero['force'] + f_b} ({hero['force']}+{f_b})      🏹 Adresse : {hero['adresse'] + a_b} ({hero['adresse']}+{a_b})

⚔️ Arme Équipée : {hero['arme']['nom']} {rarity_tag}
   💥 Dégâts de l'arme : +{hero['arme']['dmg']} | 🌟 Bonus : +{hero['arme']['stat_val']} {hero['arme']['stat'].upper()}

😂 Particularités : - {hero['particularites'][0]} | {hero['particularites'][1]}"""
    status_label.config(text=text_data)


def generate_path_choices():
    # Affiche les 3 choix de chemin
    if hero is None or hero["pv"] <= 0:
        return

    frame_chemins.pack(pady=10)
    path_left_btn.config(text=f"🚪 {random.choice(phrases_left)}")
    path_mid_btn.config(text=f"🚪 {random.choice(phrases_middle)}")
    path_right_btn.config(text=f"🚪 {random.choice(phrases_right)}")


def choose_path(direction=None):
    # Fait avancer le joueur dans une nouvelle salle
    global current_room

    if hero is None:
        return

    frame_chemins.pack_forget()
    current_room += 1
    refresh_hero_display()

    if current_room >= ROOMS_BEFORE_BOSS:
        start_boss_combat_phase()
        return

    event_roll = random.choice(["combat", "patrouille", "loot_chest", "empty_room", "trap_room", "taverne", "interaction"])

    if event_roll == "empty_room":
        log_feed.config(
            text=f"[Salle {current_room}] Vous ouvrez la porte... C'est un placard à balais géant, complètement vide. Quel sens de l'orientation tragique !",
            fg="white"
        )
        generate_path_choices()
    elif event_roll == "loot_chest":
        generate_chest_loot()
    elif event_roll == "trap_room":
        trigger_trap()
    elif event_roll == "combat":
        start_combat_phase()
    elif event_roll == "patrouille":
        trigger_patrol_event()
    elif event_roll == "taverne":
        trigger_tavern_event()
    elif event_roll == "interaction":
        trigger_interaction_event()


def trigger_trap():
    # Gère une salle-piège
    if hero is None:
        return

    total_dexterity = hero["adresse"] + (hero["arme"]["stat_val"] if hero["arme"]["stat"] == "adresse" else 0)

    if random.randint(1, 25) < total_dexterity:
        log_feed.config(
            text=f"[Salle {current_room}] Un piège s'active ! Grâce à ton ADRESSE, tu l'esquives avec élégance.",
            fg="lightgreen"
        )
    else:
        dmg = random.randint(6, 12)
        hero["pv"] -= dmg
        log_feed.config(
            text=f"[Salle {current_room}] Piège ! Un vieux dictionnaire de magie te tombe dessus ! Tu perds {dmg} PV.",
            fg="orange"
        )
        refresh_hero_display()
        evaluate_death_state()

    if hero["pv"] > 0:
        generate_path_choices()


def trigger_tavern_event():
    # Affiche l'événement taverne
    log_feed.config(
        text="🍻 SURPRISE ! Une Taverne clandestine ! 🍻\n"
             "Une odeur de bière et de graillon flotte dans l'air. Le tavernier vous dévisage.\n"
             "- Dormir sur un vieux paillasson (Coûte 15 pièces, rend tous tes PV)\n"
             "- Boire une bière tiède douteuse (Coûte 10 pièces, rend toute ta Mana)",
        fg="cyan"
    )
    frame_taverne.pack(pady=10)


def taverne_action(choix):
    # Gère le choix fait dans la taverne
    if hero is None:
        return

    frame_taverne.pack_forget()

    if choix == "dormir":
        if hero["or"] >= 15:
            hero["or"] -= 15
            hero["pv"] = hero["pv_max"]
            log_feed.config(text="Tu as dormi 20 minutes avant de te faire voler ton oreiller. Tes PV sont au max !", fg="lightgreen")
        else:
            log_feed.config(text="Pas assez de pièces ! Le videur t'éjecte d'un coup de botte.", fg="orange")

    elif choix == "biere":
        if hero["or"] >= 10:
            hero["or"] -= 10
            hero["mana"] = hero["mana_max"]
            log_feed.config(text="C'est amer, mais ton fluide magique est rechargé à bloc ! Mana restaurée.", fg="lightgreen")
        else:
            log_feed.config(text="Pas d'or, pas de picole !", fg="orange")

    refresh_hero_display()
    if hero["pv"] > 0:
        generate_path_choices()


def trigger_interaction_event():
    # Déclenche un petit événement aléatoire
    if hero is None:
        return

    inter_roll = random.choice(["statue", "marchant", "fontaine"])

    if inter_roll == "statue":
        hero["courage"] += 1
        log_feed.config(
            text=f"🗿 [Salle {current_room}] Tu examines une statue de l'Ingénieur de Naheulbeuk. Tu te sens inspiré ! (+1 COURAGE permanent)",
            fg="yellow"
        )
    elif inter_roll == "marchant":
        if hero["or"] >= 15:
            hero["or"] -= 15
            hero["pv"] = hero["pv_max"]
            hero["mana"] = hero["mana_max"]
            log_feed.config(
                text=f"🧙‍♂️ [Salle {current_room}] Un colporteur louche te vend une potion mystérieuse pour 15 pièces d'or. Tes PV et PM sont au maximum !",
                fg="lightgreen"
            )
        else:
            log_feed.config(
                text=f"🧙‍♂️ [Salle {current_room}] Un colporteur louche te propose une potion, mais tu n'as pas les 15 pièces d'or requises. Il t'insulte et s'en va.",
                fg="white"
            )
    else:
        hero["pv"] = min(hero["pv_max"], hero["pv"] + 10)
        hero["mana"] = min(hero["mana_max"], hero["mana"] + 10)
        log_feed.config(
            text=f"⛲ [Salle {current_room}] Tu bois l'eau d'une fontaine magique suspecte. Tu récupères 10 PV et 10 PM.",
            fg="cyan"
        )

    refresh_hero_display()
    generate_path_choices()


def generate_chest_loot():
    # Génère une arme aléatoire dans un coffre
    if hero is None:
        return

    rarity_roll = random.randint(1, 100)

    if rarity_roll > 90:
        tier = "Légendaire"
        nom_w = f"{random.choice(prefix_weapons)} {random.choice(suffix_legendary)}"
        dmg = random.randint(10, 16)
        buff = random.randint(4, 7)
        color = "#ff4500"
    elif rarity_roll > 60:
        tier = "Rare"
        nom_w = f"{random.choice(prefix_weapons)} {random.choice(suffix_rare)}"
        dmg = random.randint(5, 9)
        buff = random.randint(2, 4)
        color = "#1e90ff"
    else:
        tier = "Commun"
        nom_w = f"{random.choice(prefix_weapons)} {random.choice(suffix_common)}"
        dmg = random.randint(2, 4)
        buff = random.randint(1, 2)
        color = "white"

    stat = random.choice(["force", "intelligence", "adresse", "courage"])
    hero["loot_weapon"] = {
        "nom": nom_w,
        "rare": tier,
        "dmg": dmg,
        "stat": stat,
        "stat_val": buff
    }

    log = (
        f"📦 [Salle {current_room}] COFFRE TRÉSOR !\n"
        f"Un coffre en bois vermoulu t'attend.\n"
        f"Trouvé : {nom_w} [{tier}]\n"
        f"Stats : +{dmg} Dégâts | +{buff} {stat.upper()}"
    )
    log_feed.config(text=log, fg=color)
    loot_frame.pack(pady=10)


def accept_loot_weapon():
    # Équipe l'arme trouvée dans le coffre
    if hero is None or hero.get("loot_weapon") is None:
        log_feed.config(text="Aucune arme à équiper.", fg="orange")
        loot_frame.pack_forget()
        return

    hero["arme"] = hero["loot_weapon"]
    hero["loot_weapon"] = None
    log_feed.config(text=f"Tu as équipé avec fierté : {hero['arme']['nom']} !", fg="lightgreen")
    loot_frame.pack_forget()
    refresh_hero_display()
    generate_path_choices()


def discard_loot_weapon():
    # Ignore l'arme du coffre
    if hero is not None:
        hero["loot_weapon"] = None

    log_feed.config(text="Tu laisses l'arme dans le coffre.", fg="yellow")
    loot_frame.pack_forget()
    generate_path_choices()


def trigger_patrol_event():
    # Affiche l'événement patrouille
    log_feed.config(
        text="🚨 ÉVÉNEMENT : PATROUILLE EN VUE !\n"
             "Des Orcs de garde avancent en traînant des pieds dans le couloir adjacent.\n"
             "Que fait la Compagnie ?\n"
             "OPTION A : Tenter de s'esquiver en douce (Test d'ADRESSE)\n"
             "OPTION B : Charger en hurlant des insultes ! (Test de COURAGE)",
        fg="orange"
    )
    frame_evenement.pack(pady=10)


def evenement_choix(option):
    # Résout le choix fait pendant la patrouille
    if hero is None:
        return

    frame_evenement.pack_forget()

    if option == "discret":
        stat_eff = hero["adresse"] + (hero["arme"]["stat_val"] if hero["arme"]["stat"] == "adresse" else 0)
        if random.randint(1, 20) <= stat_eff:
            hero["xp"] += 20
            log_feed.config(text="Incroyable, l'Ogre n'a fait aucun bruit. Vous passez inaperçus ! (+20 XP)", fg="lightgreen")
        else:
            degats = random.randint(10, 15)
            hero["pv"] -= degats
            log_feed.config(
                text=f"Le Voleur a trébuché sur un tabouret. Les Orcs vous tirent dessus avant de sonner l'alarme ! (-{degats} PV)",
                fg="red"
            )
            evaluate_death_state()

    elif option == "baston":
        stat_eff = hero["courage"] + (hero["arme"]["stat_val"] if hero["arme"]["stat"] == "courage" else 0)
        if random.randint(1, 20) <= stat_eff:
            butin = random.randint(15, 30)
            hero["or"] += butin
            log_feed.config(text=f"Votre folie furieuse les terrorise ! Ils lâchent leur bourse et détalent. (+{butin} pièces)", fg="lightgreen")
        else:
            degats = random.randint(8, 12)
            hero["pv"] -= degats
            log_feed.config(
                text=f"La charge rate lamentablement. Vous prenez quelques coups avant de les semer. (-{degats} PV)",
                fg="red"
            )
            evaluate_death_state()

    refresh_hero_display()
    if hero["pv"] > 0:
        generate_path_choices()


# --- SYSTÈME DE COMBAT ---

def start_combat_phase():
    # Lance un combat classique
    global current_monster
    current_monster = random.choice(monsters_pool).copy()
    log_feed.config(
        text=f"💥 [Salle {current_room}] ALERTE BASTON ! {current_monster['nom']} charge ! (PV: {current_monster['pv']})",
        fg="red"
    )
    combat_frame.pack(pady=10)


def start_boss_combat_phase():
    # Lance le combat du boss final
    global current_monster
    current_monster = {"nom": "Zangdar (BOSS FINAL)", "force": 16, "pv": 65, "xp": 500}
    log_feed.config(
        text=f"👿 [SALLE 20 - BOSS] 'Par les sbires de l'enfer ! Qui foule le tapis de mon bureau ?!'\n"
             f"Le terrible {current_monster['nom']} vous attaque ! (PV: {current_monster['pv']})",
        fg="gold"
    )
    combat_frame.pack(pady=10)


def execute_enemy_counter():
    # Fait attaquer le monstre après l'action du héros
    if hero is None or current_monster is None:
        return ""

    if current_monster["pv"] > 0:
        f_totale = hero["force"] + (hero["arme"]["stat_val"] if hero["arme"]["stat"] == "force" else 0)
        dmg_m = max(1, (random.randint(2, 6) + (current_monster["force"] // 3)) - (f_totale // 6))
        hero["pv"] -= dmg_m
        refresh_hero_display()
        evaluate_death_state()
        return f"\nLe monstre riposte et t'inflige {dmg_m} dégâts !"

    return ""


def check_level_up():
    # Gère la montée de niveau du héros
    if hero is None:
        return ""

    msg_lvl = ""

    while hero["xp"] >= hero["xp_requis"]:
        hero["niveau"] += 1
        hero["xp"] -= hero["xp_requis"]
        hero["pv_max"] += 10
        hero["mana_max"] += 5
        hero["pv"] = hero["pv_max"]
        hero["mana"] = hero["mana_max"]
        msg_lvl += " 🎉 NIVEAU SUPÉRIEUR !"

        if hero["niveau"] >= 2:
            class_info = classes_data[hero["classe"]]
            skill2_btn.config(
                text=f"✨ {class_info['sort2']} ({class_info['cout2']} PM)",
                state="normal",
                bg="#4b0082"
            )

    return msg_lvl


def check_victory():
    # Vérifie si le monstre est mort
    global current_monster

    if hero is None or current_monster is None:
        return False

    if current_monster["pv"] <= 0:
        combat_frame.pack_forget()

        gains_or = random.randint(5, 15) if current_monster["nom"] != "Zangdar (BOSS FINAL)" else random.randint(100, 200)
        hero["or"] += gains_or
        hero["xp"] += current_monster["xp"]

        msg_lvl = check_level_up()
        refresh_hero_display()

        if current_monster["nom"] == "Zangdar (BOSS FINAL)":
            trigger_final_victory()
            current_monster = None
            return True

        log_feed.config(
            text=f"☠️ {current_monster['nom']} s'écroule ! Tu récupères {gains_or} pièces et {current_monster['xp']} XP.{msg_lvl}",
            fg="lightgreen"
        )
        current_monster = None
        generate_path_choices()
        return True

    return False


def execute_melee_attack():
    # Attaque de base du héros
    if hero is None or current_monster is None:
        log_feed.config(text="Aucun combat en cours.", fg="orange")
        return

    f_totale = hero["force"] + (hero["arme"]["stat_val"] if hero["arme"]["stat"] == "force" else 0)
    dmg_h = random.randint(3, 7) + (f_totale // 4) + hero["arme"]["dmg"]
    current_monster["pv"] -= dmg_h

    log = f"Tu cognes avec ton outil ({hero['arme']['nom']}) et infliges {dmg_h} dégâts."

    if not check_victory():
        log += execute_enemy_counter()
        if hero["pv"] > 0 and current_monster is not None:
            log_feed.config(text=f"{log}\n({current_monster['nom']} PV: {current_monster['pv']})", fg="pink")


def cast_skill(skill_index):
    # Lance une compétence du héros
    if hero is None or current_monster is None:
        log_feed.config(text="Aucun combat en cours.", fg="orange")
        return

    class_info = classes_data[hero["classe"]]
    skill_name = class_info[f"sort{skill_index}"]
    mana_cost = class_info[f"cout{skill_index}"]

    if skill_index == 2 and hero["niveau"] < 2:
        log_feed.config(text="Tu n'as pas encore débloqué cette compétence.", fg="orange")
        return

    if hero["mana"] < mana_cost:
        log_feed.config(text=f"Pas assez de mana pour utiliser {skill_name}.", fg="orange")
        return

    hero["mana"] -= mana_cost

    w_dmg = hero["arme"]["dmg"]
    f_t = hero["force"]
    i_t = hero["intelligence"]
    c_t = hero["courage"]

    log = f"✨ Tu lances {skill_name} ! "
    dealt_damage = False

    if skill_name == "Coup de Bouclier":
        dmg = 11 + f_t // 3 + w_dmg
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts."
        dealt_damage = True

    elif skill_name == "Exécution":
        dmg = 22 + f_t // 2
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts massifs."
        dealt_damage = True

    elif skill_name == "Soins Mineurs":
        heal = 17 + i_t // 2
        hero["pv"] = min(hero["pv_max"], hero["pv"] + heal)
        log += f"Tu récupères {heal} PV."

    elif skill_name == "Colère Divine":
        dmg = 20 + i_t
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts sacrés."
        dealt_damage = True

    elif skill_name == "Boule de Feu":
        dmg = 20 + i_t
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts enflammés."
        dealt_damage = True

    elif skill_name == "Éclair Enchaîné":
        dmg = 25 + i_t
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts électriques."
        dealt_damage = True

    elif skill_name == "Attaque Sournoise":
        dmg = 6 if random.randint(1, 4) == 1 else 25 + w_dmg
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts perfides."
        dealt_damage = True

    elif skill_name == "Lame Toxique":
        dmg = 6 if random.randint(1, 4) == 1 else 25 + w_dmg
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts empoisonnés."
        dealt_damage = True

    elif skill_name == "Justice Divine":
        dmg = 14 + c_t // 3
        heal = 5
        current_monster["pv"] -= dmg
        hero["pv"] = min(hero["pv_max"], hero["pv"] + heal)
        log += f"{dmg} dégâts et {heal} PV restaurés."
        dealt_damage = True

    elif skill_name == "Bouclier Lumineux":
        dmg = 14 + c_t // 3
        heal = 6
        current_monster["pv"] -= dmg
        hero["pv"] = min(hero["pv_max"], hero["pv"] + heal)
        log += f"{dmg} dégâts et {heal} PV restaurés."
        dealt_damage = True

    elif skill_name == "Tir Précis":
        dmg = 14 + w_dmg
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts précis."
        dealt_damage = True

    elif skill_name == "Pluie de Flèches":
        dmg = 20 + w_dmg
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts à distance."
        dealt_damage = True

    elif skill_name == "Esprit Totem":
        dmg = 15 + c_t
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts mystico-absurdes."
        dealt_damage = True

    elif skill_name == "Flûte Insupportable":
        dmg = 16 + w_dmg
        current_monster["pv"] -= dmg
        log += f"{dmg} dégâts sonores."
        dealt_damage = True

    else:
        log += "Mais il ne se passe rien d'utile."

    refresh_hero_display()

    if dealt_damage and check_victory():
        return

    log += execute_enemy_counter()
    refresh_hero_display()

    if hero["pv"] > 0 and current_monster is not None:
        log_feed.config(text=f"{log}\n({current_monster['nom']} PV: {current_monster['pv']})", fg="violet")


def execute_flee_action():
    # Tente de fuir un combat
    global current_monster

    if hero is None or current_monster is None:
        log_feed.config(text="Aucun combat en cours.", fg="orange")
        return

    if current_monster["nom"] == "Zangdar (BOSS FINAL)":
        log_feed.config(text="Impossible de fuir face au boss final. Ce serait trop facile.", fg="orange")
        return

    flee_stat = hero["adresse"] + (hero["arme"]["stat_val"] if hero["arme"]["stat"] == "adresse" else 0)

    if random.randint(1, 20) <= flee_stat:
        combat_frame.pack_forget()
        log_feed.config(text="🏃 Tu prends tes jambes à ton cou et disparais dans le couloir !", fg="lightgreen")
        current_monster = None
        generate_path_choices()
    else:
        log = "🏃 Tu tentes de fuir, mais tu glisses sur un truc visqueux."
        log += execute_enemy_counter()
        if hero["pv"] > 0 and current_monster is not None:
            log_feed.config(text=log, fg="orange")


# --- FIN DE PARTIE ---

def trigger_final_victory():
    # Affiche la victoire finale avec image si disponible
    global victory_image_ref

    combat_frame.pack_forget()
    loot_frame.pack_forget()
    frame_chemins.pack_forget()
    frame_taverne.pack_forget()
    frame_evenement.pack_forget()

    image_ok = show_end_image(victory_image_ref)

    if image_ok:
        log_feed.config(
            text="🎉 VICTOIRE HISTORIQUE ! Tu as terrassé Zangdar et récupéré la douzième statuette de Gladeulfeurha !",
            fg="gold"
        )
    else:
        img_path = os.path.join(SCRIPT_DIR, "victoire.png")
        log_feed.config(
            text=f"🎉 VICTOIRE ! Image impossible à afficher.\nChemin testé : {img_path}",
            fg="gold"
        )

    reset_btn.pack(pady=10)


def evaluate_death_state():
    # Vérifie si le héros est mort et affiche l'image de game over si possible
    global gameover_image_ref

    if hero is None:
        return

    if hero["pv"] <= 0:
        hero["pv"] = 0
        refresh_hero_display()

        combat_frame.pack_forget()
        loot_frame.pack_forget()
        frame_chemins.pack_forget()
        frame_taverne.pack_forget()
        frame_evenement.pack_forget()

        image_ok = show_end_image(gameover_image_ref)

        if image_ok:
            log_feed.config(
                text=f"💀 Tu as succombé à la salle {current_room}. Fin de la compagnie. GAME OVER.",
                fg="red"
            )
        else:
            img_path = os.path.join(SCRIPT_DIR, "gameover.png")
            log_feed.config(
                text=f"💀 GAME OVER ! Image impossible à afficher.\nChemin testé : {img_path}",
                fg="red"
            )

        reset_btn.pack(pady=10)


def return_to_menu():
    # Réinitialise totalement la partie
    global hero, current_monster, current_room, image_display_label

    hero = None
    current_monster = None
    current_room = 0

    combat_frame.pack_forget()
    loot_frame.pack_forget()
    frame_chemins.pack_forget()
    frame_taverne.pack_forget()
    frame_evenement.pack_forget()
    reset_btn.pack_forget()
    status_label.pack_forget()

    if image_display_label is not None:
        image_display_label.destroy()
        image_display_label = None

    entree_nom.delete(0, tk.END)
    log_feed.config(text="Bienvenue dans le Donjon de Naheulbeuk. Crée ton aventurier.", fg="white")
    frame_menu_creation.pack(pady=10)


# --- FENÊTRE PRINCIPALE ---
window = tk.Tk()
window.title("Le Donjon de Naheulbeuk")
window.geometry("1100x760")
window.configure(bg="#2d1b0f")

# Chargement des images après création de la fenêtre Tk
# C'est plus fiable pour ImageTk.PhotoImage
victory_image_ref = load_game_image("victoire.png")
gameover_image_ref = load_game_image("gameover.png")

title_label = tk.Label(
    window,
    text="🏰 LE DONJON DE NAHEULBEUK 🏰",
    font=("Arial", 20, "bold"),
    bg="#2d1b0f",
    fg="gold"
)
title_label.pack(pady=10)

log_feed = tk.Label(
    window,
    text="Bienvenue dans le Donjon de Naheulbeuk. Crée ton aventurier.",
    font=("Arial", 12),
    bg="#2d1b0f",
    fg="white",
    justify="left",
    wraplength=950
)
log_feed.pack(pady=10)

status_label = tk.Label(
    window,
    text="",
    font=("Courier", 11),
    bg="#1a1a1a",
    fg="#dcdcdc",
    justify="left",
    anchor="w"
)

# --- MENU DE CRÉATION ---
frame_menu_creation = tk.Frame(window, bg="#2d1b0f")
frame_menu_creation.pack(pady=10)

frame_input = tk.Frame(frame_menu_creation, bg="#2d1b0f")
frame_input.pack(pady=5)

lbl_nom = tk.Label(frame_input, text="Nom :", font=("Arial", 11, "bold"), bg="#2d1b0f", fg="white")
lbl_nom.pack(side="left", padx=5)

entree_nom = tk.Entry(frame_input, font=("Arial", 11), width=25)
entree_nom.pack(side="left", padx=5)

btn_creer = tk.Button(
    frame_input,
    text="🧙 Créer Aventurier",
    font=("Arial", 11, "bold"),
    command=generate_character,
    bg="#8b4513",
    fg="white"
)
btn_creer.pack(side="left", padx=5)

frame_genre = tk.Frame(frame_menu_creation, bg="#2d1b0f")
frame_genre.pack(pady=2)

male_btn = tk.Button(frame_genre, text="👨 Homme", command=lambda: choose_gender("homme", male_btn))
male_btn.pack(side="left", padx=5)

female_btn = tk.Button(frame_genre, text="👩 Femme", command=lambda: choose_gender("femme", female_btn))
female_btn.pack(side="left", padx=5)

rand_g_btn = tk.Button(frame_genre, text="🎲 Aléatoire", bg="gold", command=lambda: choose_gender("Aléatoire", rand_g_btn))
rand_g_btn.pack(side="left", padx=5)

frame_race = tk.Frame(frame_menu_creation, bg="#2d1b0f")
frame_race.pack(pady=2)

for r_node in races:
    r_btn = tk.Button(frame_race, text=r_node)
    r_btn.config(command=lambda r=r_node, b=r_btn: choose_race(r, b))
    r_btn.pack(side="left", padx=2)

rand_r_btn = tk.Button(frame_race, text="🎲 Aléatoire", bg="#32cd32", fg="white", command=lambda: choose_race("Aléatoire", rand_r_btn))
rand_r_btn.pack(side="left", padx=2)

frame_classe = tk.Frame(frame_menu_creation, bg="#2d1b0f")
frame_classe.pack(pady=2)

for c_node in classes:
    c_btn = tk.Button(frame_classe, text=c_node)
    c_btn.config(command=lambda c=c_node, b=c_btn: choose_class(c, b))
    c_btn.pack(side="left", padx=2)

rand_c_btn = tk.Button(frame_classe, text="🎲 Aléatoire", bg="#32cd32", fg="white", command=lambda: choose_class("Aléatoire", rand_c_btn))
rand_c_btn.pack(side="left", padx=2)

# --- CHOIX DES CHEMINS ---
frame_chemins = tk.Frame(window, bg="#2d1b0f")

path_left_btn = tk.Button(frame_chemins, text="", font=("Arial", 11), width=24, bg="#5c4033", fg="white", command=lambda: choose_path("left"))
path_left_btn.pack(side="left", padx=5)

path_mid_btn = tk.Button(frame_chemins, text="", font=("Arial", 11), width=24, bg="#5c4033", fg="white", command=lambda: choose_path("middle"))
path_mid_btn.pack(side="left", padx=5)

path_right_btn = tk.Button(frame_chemins, text="", font=("Arial", 11), width=24, bg="#5c4033", fg="white", command=lambda: choose_path("right"))
path_right_btn.pack(side="left", padx=5)

# --- COMBAT ---
combat_frame = tk.Frame(window, bg="#2d1b0f")

attack_btn = tk.Button(combat_frame, text="⚔️ ATTAQUER", font=("Arial", 11, "bold"), bg="#8b0000", fg="white", width=12, command=execute_melee_attack)
attack_btn.pack(side="left", padx=4)

skill1_btn = tk.Button(combat_frame, text="", font=("Arial", 11, "bold"), bg="#4b0082", fg="white", width=22, command=lambda: cast_skill(1))
skill1_btn.pack(side="left", padx=4)

skill2_btn = tk.Button(combat_frame, text="", font=("Arial", 11, "bold"), bg="grey", fg="white", width=22, command=lambda: cast_skill(2))
skill2_btn.pack(side="left", padx=4)

flee_btn = tk.Button(combat_frame, text="🏃 FUIR", font=("Arial", 11, "bold"), bg="orange", fg="black", width=10, command=execute_flee_action)
flee_btn.pack(side="left", padx=4)

# --- LOOT ---
loot_frame = tk.Frame(window, bg="#2d1b0f")

equip_btn = tk.Button(loot_frame, text="🎒 ÉQUIPER", font=("Arial", 12, "bold"), bg="#4a7c59", fg="white", width=12, command=accept_loot_weapon)
equip_btn.pack(side="left", padx=5)

discard_btn = tk.Button(loot_frame, text="🗑️ JETER", font=("Arial", 12, "bold"), bg="#8b0000", fg="white", width=12, command=discard_loot_weapon)
discard_btn.pack(side="left", padx=5)

# --- TAVERNE ---
frame_taverne = tk.Frame(window, bg="#2d1b0f")

btn_dormir = tk.Button(frame_taverne, text="🛌 Dormir (15 Or)", font=("Arial", 11, "bold"), bg="#4a7c59", fg="white", command=lambda: taverne_action("dormir"))
btn_dormir.pack(side="left", padx=5)

btn_biere = tk.Button(frame_taverne, text="🍺 Bière (10 Or)", font=("Arial", 11, "bold"), bg="#1e90ff", fg="white", command=lambda: taverne_action("biere"))
btn_biere.pack(side="left", padx=5)

# --- ÉVÉNEMENT PATROUILLE ---
frame_evenement = tk.Frame(window, bg="#2d1b0f")

btn_discret = tk.Button(frame_evenement, text="🕵️ Option A (Discrétion)", font=("Arial", 11, "bold"), bg="#4b0082", fg="white", command=lambda: evenement_choix("discret"))
btn_discret.pack(side="left", padx=5)

btn_baston = tk.Button(frame_evenement, text="🪓 Option B (Froncer)", font=("Arial", 11, "bold"), bg="#8b0000", fg="white", command=lambda: evenement_choix("baston"))
btn_baston.pack(side="left", padx=5)

# --- RESET ---
reset_btn = tk.Button(
    window,
    text="🔄 Retourner au Menu Principal",
    font=("Arial", 12, "bold"),
    bg="#20b2aa",
    fg="white",
    command=return_to_menu
)

# --- LANCEMENT DE L'APPLICATION ---
window.mainloop()
