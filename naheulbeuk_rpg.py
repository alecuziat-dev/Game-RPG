import tkinter as tk
import random
import os
import json
import time
from PIL import Image, ImageTk

try:
    import pygame
    AUDIO_LIB_AVAILABLE = True
except ImportError:
    AUDIO_LIB_AVAILABLE = False

# --- JEU : LE DONJON DE NAHEULBEUK ---
# Interface graphique Tkinter pour un mini-RPG textuel.

# Dossier du script pour retrouver les images
# Si __file__ n'existe pas selon l'environnement, on prend le dossier courant
if "__file__" in globals():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    SCRIPT_DIR = os.getcwd()

SAVE_SLOTS = 3


def get_save_path(slot):
    return os.path.join(SCRIPT_DIR, f"sauvegarde_naheulbeuk_slot{slot}.json")

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

ROOMS_BEFORE_BOSS = 30
MIDBOSS_ROOM = 15

selected_gender = "Aléatoire"
selected_race = "Aléatoire"
selected_class = "Aléatoire"
selected_difficulty = "Normal"

AUDIO_READY = False
music_muted = False
current_track = None  # "ambiance" ou "combat", pour éviter de relancer le même morceau en boucle

DIFFICULTY_SCALING = {
    "Facile": 0.75,
    "Normal": 1.0,
    "Difficile": 1.3,
}

# --- DONNÉES DE BASE ---
races = ["Humain", "Ogre", "Elfe", "Thérianthropes", "Nain", "Elfe noir", "Orc"]

# Bonus de statistiques propres à chaque race (ajoutés après les bonus de classe)
race_bonus = {
    "Humain":          {"force": 1, "intelligence": 1, "adresse": 1, "courage": 1},
    "Ogre":            {"force": 4},
    "Elfe":            {"intelligence": 2, "adresse": 1},
    "Thérianthropes":  {"force": 2, "adresse": 1},
    "Nain":            {"force": 2, "courage": 1},
    "Elfe noir":       {"adresse": 2, "courage": 1},
    "Orc":             {"force": 2, "courage": 1},
}

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

# Icônes et couleurs pour le portrait visuel du héros
class_icons = {
    "Guerrier": "⚔️", "Évêque": "✝️", "Mage": "🔮", "Assassin": "🗡️",
    "Paladin": "🛡️", "Ranger": "🏹", "Barde": "🎵",
}
race_colors = {
    "Humain": "#8b7355", "Ogre": "#556b2f", "Elfe": "#2e8b57",
    "Thérianthropes": "#8b4513", "Nain": "#4682b4", "Elfe noir": "#483d8b", "Orc": "#6b4226",
}
rarity_colors = {"Commun": "#888888", "Rare": "#1e90ff", "Légendaire": "#ff4500"}

# Si un fichier "<slug_race>_h.png" ou "<slug_race>_f.png" existe dans le dossier du script,
# il remplace automatiquement le portrait généré (cercle + icône) pour cette race et ce genre.
race_portrait_slug = {
    "Humain": "Humain",
    "Ogre": "Ogre",
    "Elfe": "Elfe",
    "Thérianthropes": "Thérianthrope",
    "Nain": "Nain",
    "Elfe noir": "Elfe_noir",
    "Orc": "Orc",
}
portrait_image_ref = None
race_thumbnail_refs = {}  # {race: PhotoImage} - garde les vignettes du menu en mémoire
race_buttons = {}  # {race: bouton} - rempli à la création des widgets, pour mettre à jour leur image


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
    {"nom": "Zombie administratif", "force": 12, "pv": 30, "xp": 45},
    {"nom": "Rat des égouts géant", "force": 7, "pv": 16, "xp": 20},
    {"nom": "Kobold paperassier", "force": 9, "pv": 20, "xp": 28},
    {"nom": "Araignée cracheuse", "force": 11, "pv": 25, "xp": 38},
    {"nom": "Troll des cavernes", "force": 14, "pv": 34, "xp": 55},
    {"nom": "Sorcier raté", "force": 10, "pv": 22, "xp": 32},
    {"nom": "Harpie criarde", "force": 12, "pv": 27, "xp": 42},
    {"nom": "Golem d'argile fendu", "force": 15, "pv": 36, "xp": 58},
]

# --- ÉQUIPEMENT & CONSOMMABLES (marchand) ---
armure_catalog = [
    {"nom": "Gilet de cuir bouilli", "rare": "Commun", "def": 2, "stat": "courage", "stat_val": 1, "prix": 20},
    {"nom": "Cotte de mailles rouillée", "rare": "Rare", "def": 4, "stat": "force", "stat_val": 1, "prix": 45},
    {"nom": "Plastron renforcé", "rare": "Légendaire", "def": 7, "stat": "force", "stat_val": 2, "prix": 90},
]
casque_catalog = [
    {"nom": "Bonnet matelassé", "rare": "Commun", "def": 1, "stat": "intelligence", "stat_val": 1, "prix": 12},
    {"nom": "Casque à cornes ébréché", "rare": "Rare", "def": 3, "stat": "courage", "stat_val": 1, "prix": 35},
    {"nom": "Heaume de fer", "rare": "Légendaire", "def": 5, "stat": "courage", "stat_val": 2, "prix": 70},
]
bottes_catalog = [
    {"nom": "Sandales trouées", "rare": "Commun", "def": 1, "stat": "adresse", "stat_val": 1, "prix": 10},
    {"nom": "Bottes de marche renforcées", "rare": "Rare", "def": 2, "stat": "adresse", "stat_val": 1, "prix": 30},
    {"nom": "Bottes cloutées", "rare": "Légendaire", "def": 4, "stat": "adresse", "stat_val": 2, "prix": 55},
]
consumable_catalog = [
    {"nom": "Potion de Soin", "type": "potion", "prix": 15},
    {"nom": "Ration de Voyage", "type": "nourriture", "prix": 8},
    {"nom": "Fiole de Mana", "type": "mana", "prix": 12},
]

# --- FONCTIONS UTILITAIRES ---

image_load_errors = {}  # {nom_de_fichier_demandé: message d'erreur} pour affichage en jeu


def load_game_image(filename, size=(650, 320)):
    # Charge une image depuis le dossier du script
    # Retourne une PhotoImage si tout va bien, sinon None (le détail de l'échec est gardé dans image_load_errors)
    image_load_errors.pop(filename, None)
    img_path = os.path.join(SCRIPT_DIR, filename)

    if not os.path.exists(img_path):
        # Le fichier exact n'existe pas : on cherche une variante tolérante
        # (casse différente : "Victoire.PNG", et/ou extension différente : .jpg, .jpeg, .bmp, .gif)
        base_name = os.path.splitext(filename)[0].lower()
        candidates = []
        try:
            for f in os.listdir(SCRIPT_DIR):
                name_no_ext, ext = os.path.splitext(f)
                if name_no_ext.lower() == base_name and ext.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
                    candidates.append(f)
        except OSError:
            candidates = []

        if candidates:
            img_path = os.path.join(SCRIPT_DIR, candidates[0])
            print(f"Image trouvée via correspondance tolérante : {img_path}")
        else:
            msg = f"fichier introuvable dans {SCRIPT_DIR}"
            image_load_errors[filename] = msg
            print(f"Image introuvable : {img_path}")
            print(f"   -> Vérifie que le fichier est bien dans le dossier : {SCRIPT_DIR}")
            return None

    try:
        pil_img = Image.open(img_path)
        pil_img = pil_img.convert("RGB")
        pil_img = pil_img.resize(size, RESAMPLE)
        return ImageTk.PhotoImage(pil_img)
    except Exception as e:
        image_load_errors[filename] = f"{type(e).__name__}: {e}"
        print(f"Erreur lors du chargement de {img_path} : {e}")
        return None


def find_asset_file(base_name, extensions):
    # Cherche un fichier "base_name.ext" dans le dossier du script, tolérant à la casse et à l'extension
    for ext in extensions:
        direct_path = os.path.join(SCRIPT_DIR, base_name + ext)
        if os.path.exists(direct_path):
            return direct_path

    base_lower = base_name.lower()
    try:
        for f in os.listdir(SCRIPT_DIR):
            name_no_ext, ext = os.path.splitext(f)
            if name_no_ext.lower() == base_lower and ext.lower() in extensions:
                return os.path.join(SCRIPT_DIR, f)
    except OSError:
        pass

    return None


def load_portrait_image(base_name, size=(84, 84)):
    # Charge une image de portrait perso (PNG/JPG/...), en conservant la transparence si présente
    path = find_asset_file(base_name, (".png", ".jpg", ".jpeg", ".gif", ".bmp"))
    if path is None:
        return None
    try:
        pil_img = Image.open(path)
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        pil_img = pil_img.resize(size, RESAMPLE)
        return ImageTk.PhotoImage(pil_img)
    except Exception as e:
        print(f"Erreur lors du chargement du portrait ({path}) : {e}")
        return None


def init_audio():
    # Initialise le mixer audio si pygame est installé. Ne bloque jamais le jeu en cas d'échec.
    global AUDIO_READY
    if not AUDIO_LIB_AVAILABLE:
        print("🔇 Musique désactivée : le module 'pygame' n'est pas installé (pip install pygame).")
        return
    try:
        pygame.mixer.init()
        AUDIO_READY = True
    except Exception as e:
        print(f"🔇 Musique désactivée : impossible d'initialiser l'audio ({e}).")
        AUDIO_READY = False


def play_music(base_name, volume=0.4, track_id=None):
    # Joue en boucle le premier fichier trouvé pour base_name (.mp3/.ogg/.wav), sans jamais planter le jeu
    global current_track
    if not AUDIO_READY:
        return

    if track_id is not None and track_id == current_track:
        return  # déjà en train de jouer ce morceau, on ne relance pas depuis le début

    current_track = track_id

    if music_muted:
        return  # on retient le morceau "logique" en cours, mais on ne joue rien tant que c'est coupé

    path = find_asset_file(base_name, (".mp3", ".ogg", ".wav"))
    if path is None:
        print(f"🔇 Musique introuvable : {base_name} (.mp3/.ogg/.wav) dans {SCRIPT_DIR}")
        return

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=-1)
    except Exception as e:
        print(f"🔇 Erreur de lecture audio ({path}) : {e}")


def play_ambient_music():
    play_music("musique_ambiance", volume=0.35, track_id="ambiance")


def play_combat_music():
    play_music("musique_combat", volume=0.45, track_id="combat")


def stop_music():
    global current_track
    if AUDIO_READY:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    current_track = None


def toggle_music_mute():
    # Coupe ou réactive la musique sans perdre la mémoire du morceau qui devrait jouer
    global music_muted, current_track
    music_muted = not music_muted

    if music_muted:
        if AUDIO_READY:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        mute_btn.config(text="🔇")
    else:
        mute_btn.config(text="🔊")
        track_to_restore = current_track
        current_track = None  # force play_music à relancer réellement le morceau
        if track_to_restore == "combat":
            play_combat_music()
        elif track_to_restore == "ambiance":
            play_ambient_music()


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


def animate_dice_roll(final_value, max_value, success, on_complete):
    # Affiche une petite fenêtre avec un dé qui "roule" visuellement avant de
    # s'arrêter sur le résultat final_value (sur max_value), coloré selon succès/échec.
    # Appelle on_complete() une fois l'animation terminée.
    dice_popup = tk.Toplevel(window)
    dice_popup.title("🎲 Jet de dé")
    dice_popup.configure(bg="#2d1b0f")
    dice_popup.geometry("220x230")
    dice_popup.resizable(False, False)
    try:
        dice_popup.transient(window)
        dice_popup.grab_set()
    except tk.TclError:
        pass

    tk.Label(dice_popup, text=f"🎲 Jet sur {max_value}", font=("Arial", 11, "bold"), bg="#2d1b0f", fg="white").pack(pady=(10, 4))

    canvas = tk.Canvas(dice_popup, width=160, height=160, bg="#1a1a1a", highlightthickness=0)
    canvas.pack(pady=4)

    result_lbl = tk.Label(dice_popup, text="...", font=("Arial", 11, "bold"), bg="#2d1b0f", fg="white")
    result_lbl.pack(pady=(2, 8))

    def draw_die(value, color="white"):
        canvas.delete("all")
        canvas.create_rectangle(15, 15, 145, 145, outline=color, width=4, fill="#2d1b0f")
        canvas.create_text(80, 80, text=str(value), font=("Arial", 40, "bold"), fill=color)

    state = {"ticks": 0}

    def tick():
        state["ticks"] += 1
        if state["ticks"] < 9:
            draw_die(random.randint(1, max_value), "white")
            dice_popup.after(55, tick)
        else:
            color = "#32cd32" if success else "#ff4500"
            draw_die(final_value, color)
            result_lbl.config(text=("✅ RÉUSSITE !" if success else "❌ ÉCHEC..."), fg=color)
            dice_popup.after(650, finish)

    def finish():
        try:
            dice_popup.grab_release()
        except tk.TclError:
            pass
        try:
            dice_popup.destroy()
        except tk.TclError:
            pass
        on_complete()

    tick()


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


def choose_difficulty(difficulty, clicked_btn):
    # Sélection de la difficulté (ajuste le scaling des monstres et boss)
    global selected_difficulty
    selected_difficulty = difficulty
    for b in frame_difficulte.winfo_children():
        b.config(bg="#f0f0f0", fg="black")
    clicked_btn.config(bg="#ff8c00", fg="white")


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

    # Bonus racial (en plus du bonus de classe)
    r_bonus = race_bonus.get(race, {})
    strength += r_bonus.get("force", 0)
    intelligence += r_bonus.get("intelligence", 0)
    dexterity += r_bonus.get("adresse", 0)
    courage += r_bonus.get("courage", 0)

    hero = {
        "nom": name,
        "genre": gender,
        "race": race,
        "classe": char_class,
        "difficulte": selected_difficulty,
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
        "equipement": {"armure": None, "casque": None, "bottes": None},
        "consommables": {"potion": 1, "nourriture": 1, "mana": 1},
        "loot_item": None,
        "inventaire": [],
        "stats": {"monstres_tues": 0, "or_gagne": 20, "temps_debut": time.time()}
    }

    frame_menu_creation.pack_forget()
    status_label.pack(fill="x", padx=40, pady=5)
    hero_display_frame.pack(pady=4)
    dungeon_map_canvas.pack(pady=6)
    inv_btn.pack(pady=4)
    save_btn.pack(pady=2)
    quit_btn.pack(pady=2)
    refresh_inventory_button()
    refresh_hero_display()

    refresh_skill_buttons()

    log_feed.config(text=f"{hero['nom']} entre dans le donjon. Mauvaise idée, excellent divertissement.", fg="white")
    generate_path_choices()


def refresh_skill_buttons():
    # Synchronise l'affichage des boutons de compétence avec la classe et le niveau du héros
    if hero is None:
        return
    class_info = classes_data[hero["classe"]]
    skill1_btn.config(text=f"✨ {class_info['sort1']} ({class_info['cout1']} PM)")
    if hero["niveau"] >= 2:
        skill2_btn.config(text=f"✨ {class_info['sort2']} ({class_info['cout2']} PM)", state="normal", bg="#4b0082")
    else:
        skill2_btn.config(text=f"🔒 {class_info['sort2']} (Niv 2)", state="disabled", bg="grey")


def get_effective_stat(stat_name):
    # Renvoie la stat du héros augmentée des bonus de son arme et de tout son équipement
    if hero is None:
        return 0
    total = hero[stat_name]
    if hero["arme"]["stat"] == stat_name:
        total += hero["arme"]["stat_val"]
    for slot in ("armure", "casque", "bottes"):
        item = hero.get("equipement", {}).get(slot)
        if item and item.get("stat") == stat_name:
            total += item.get("stat_val", 0)
    return total


def get_total_defense():
    # Somme la défense apportée par toutes les pièces d'équipement portées
    if hero is None:
        return 0
    total = 0
    for slot in ("armure", "casque", "bottes"):
        item = hero.get("equipement", {}).get(slot)
        if item:
            total += item.get("def", 0)
    return total


def add_gold(amount):
    # Ajoute de l'or au héros en suivant le total gagné sur la partie (pour l'écran de fin)
    if hero is None:
        return
    hero["or"] += amount
    hero["stats"]["or_gagne"] += amount


def apply_damage_to_hero(raw_dmg):
    # Applique des dégâts au héros en tenant compte de la réduction d'armure (1 dégât minimum)
    if hero is None:
        return 0
    dmg = max(1, raw_dmg - get_total_defense())
    hero["pv"] -= dmg
    flash_hit_effect()
    return dmg


def flash_hit_effect():
    # Effet visuel bref (flash rouge sur la barre de PV) quand le héros encaisse un coup.
    # Le dessin est différé pour s'exécuter après le rafraîchissement normal de la fiche,
    # sinon il serait immédiatement effacé par le prochain refresh_hero_bars().
    def show_flash():
        try:
            hero_bars_canvas.create_rectangle(0, 0, 860, 26, fill="#ff0000", tags="hit_flash")
            window.after(140, lambda: hero_bars_canvas.delete("hit_flash"))
        except tk.TclError:
            pass

    try:
        window.after(20, show_flash)
    except tk.TclError:
        pass


def draw_bar(canvas, x, y, width, height, value, max_value, fill_color, prefix):
    # Dessine une barre de progression avec fond, remplissage proportionnel et texte incrusté
    ratio = 0 if max_value <= 0 else max(0, min(1, value / max_value))
    canvas.create_rectangle(x, y, x + width, y + height, fill="#1a1a1a", outline="#5c4033", width=1)
    if ratio > 0:
        canvas.create_rectangle(x, y, x + width * ratio, y + height, fill=fill_color, outline="")
    canvas.create_text(x + 8, y + height / 2, text=f"{prefix} {value}/{max_value}", fill="white", font=("Arial", 10, "bold"), anchor="w")


def refresh_hero_bars():
    # Redessine les barres de PV / Mana / XP du héros
    if hero is None:
        return

    hero_bars_canvas.delete("all")
    width, height, gap, x = 940, 22, 6, 10

    pv_ratio = hero["pv"] / hero["pv_max"] if hero["pv_max"] else 0
    if pv_ratio > 0.5:
        pv_color = "#2e8b57"
    elif pv_ratio > 0.25:
        pv_color = "#ff8c00"
    else:
        pv_color = "#b22222"

    draw_bar(hero_bars_canvas, x, 4, width, height, hero["pv"], hero["pv_max"], pv_color, "❤️ PV")
    draw_bar(hero_bars_canvas, x, 4 + (height + gap), width, height, hero["mana"], hero["mana_max"], "#4169e1", "🔮 MANA")
    draw_bar(hero_bars_canvas, x, 4 + 2 * (height + gap), width, height, hero["xp"], hero["xp_requis"], "#9370db", "✨ XP")


def refresh_race_thumbnails():
    # Choisit aléatoirement une version homme/femme du portrait de chaque race
    # pour illustrer les boutons de sélection dans le menu de création
    for race in races:
        slug = race_portrait_slug.get(race)
        if not slug:
            continue

        gender_suffix = random.choice(["h", "f"])
        img = load_portrait_image(f"{slug}_{gender_suffix}", size=(48, 48))
        if img is not None:
            race_thumbnail_refs[race] = img
            btn = race_buttons.get(race)
            if btn is not None:
                btn.config(image=img, compound="top")


def refresh_portrait():
    # Dessine le portrait du héros : une image fournie par le joueur si disponible,
    # sinon un portrait généré (cercle coloré par race + icône de classe)
    global portrait_image_ref

    portrait_canvas.delete("all")
    if hero is None:
        return

    slug = race_portrait_slug.get(hero["race"])
    gender_suffix = "h" if hero["genre"] == "homme" else "f"
    base_name = f"{slug}_{gender_suffix}" if slug else None
    img_ref = load_portrait_image(base_name, size=(84, 84)) if base_name else None

    if img_ref is not None:
        portrait_image_ref = img_ref  # garder une référence pour éviter le nettoyage mémoire
        portrait_canvas.create_image(45, 45, image=portrait_image_ref)
        portrait_canvas.create_oval(4, 4, 86, 86, outline="gold", width=3)
    else:
        bg_color = race_colors.get(hero["race"], "#5c4033")
        portrait_canvas.create_oval(4, 4, 86, 86, fill=bg_color, outline="gold", width=3)
        icon = class_icons.get(hero["classe"], "❔")
        portrait_canvas.create_text(45, 42, text=icon, font=("Arial", 30))

    portrait_canvas.create_rectangle(15, 68, 75, 88, fill="#000000", outline="")
    portrait_canvas.create_text(45, 78, text=f"Niv.{hero['niveau']}", fill="white", font=("Arial", 9, "bold"))


def refresh_equipment_icons():
    # Affiche l'arme et l'équipement porté sous forme de pastilles colorées par rareté
    equipment_icons_canvas.delete("all")
    if hero is None:
        return

    equip = hero.get("equipement", {"armure": None, "casque": None, "bottes": None})
    slots = [
        ("⚔️", hero["arme"]),
        ("🥋", equip.get("armure")),
        ("⛑️", equip.get("casque")),
        ("🥾", equip.get("bottes")),
    ]

    box_w, box_h, gap, x, y = 205, 46, 6, 0, 4

    for icon, item in slots:
        if item:
            color = rarity_colors.get(item.get("rare", "Commun"), "#888888")
            name = item["nom"]
            if len(name) > 16:
                name = name[:14] + "…"
        else:
            color = "#3e2a17"
            name = "-- vide --"

        equipment_icons_canvas.create_rectangle(x, y, x + box_w, y + box_h, fill="#1a1a1a", outline=color, width=3)
        equipment_icons_canvas.create_text(x + 20, y + box_h / 2, text=icon, font=("Arial", 15))
        equipment_icons_canvas.create_text(x + 38, y + box_h / 2, text=name, fill="white", font=("Arial", 9, "bold"), anchor="w")
        x += box_w + gap


def refresh_monster_bar():
    # Redessine la barre de vie du monstre affrontée en combat (avec indicateur d'enrage pour les boss)
    monster_bar_canvas.delete("all")
    if current_monster is None:
        return

    width, height, x, y = 940, 24, 10, 6
    pv_ratio = current_monster["pv"] / current_monster["pv_max"] if current_monster["pv_max"] else 0

    if current_monster.get("enrage"):
        color = "#8b0000"
    elif pv_ratio > 0.5:
        color = "#4a7c59"
    elif pv_ratio > 0.25:
        color = "#ff8c00"
    else:
        color = "#b22222"

    label = current_monster["nom"]
    if current_monster.get("enrage"):
        label += " 🔥 ENRAGÉ"

    draw_bar(monster_bar_canvas, x, y, width, height, max(0, current_monster["pv"]), current_monster["pv_max"], color, label)


def refresh_hero_display():
    # Met à jour la fiche du héros
    if hero is None:
        return

    f_b = get_effective_stat("force") - hero["force"]
    i_b = get_effective_stat("intelligence") - hero["intelligence"]
    a_b = get_effective_stat("adresse") - hero["adresse"]
    c_b = get_effective_stat("courage") - hero["courage"]

    rarity_tag = f"[{hero['arme']['rare']}]"
    defense_totale = get_total_defense()

    conso = hero.get("consommables", {"potion": 0, "nourriture": 0})

    text_data = f"""📇 FICHE D'AVENTURIER (Niveau {hero['niveau']}) | 🏰 Salle : {current_room}/{ROOMS_BEFORE_BOSS} | 🪙 OR : {hero['or']} pièces 📇
Nom : {hero['nom']} ({hero['genre']}) - {hero['race']} {hero['classe']}

⚔ Courage : {hero['courage'] + c_b} ({hero['courage']}+{c_b})   🧠 Intelligence : {hero['intelligence'] + i_b} ({hero['intelligence']}+{i_b})
💪 Force : {hero['force'] + f_b} ({hero['force']}+{f_b})      🏹 Adresse : {hero['adresse'] + a_b} ({hero['adresse']}+{a_b})      🛡️ Défense : {defense_totale}

⚔️ Arme : {hero['arme']['nom']} {rarity_tag} (+{hero['arme']['dmg']} Dégâts | +{hero['arme']['stat_val']} {hero['arme']['stat'].upper()})
🧪 Potions : {conso.get('potion', 0)}   🍖 Rations : {conso.get('nourriture', 0)}   🔮 Fioles de Mana : {conso.get('mana', 0)}

😂 Particularités : - {hero['particularites'][0]} | {hero['particularites'][1]}"""
    status_label.config(text=text_data)

    refresh_portrait()
    refresh_equipment_icons()

    refresh_hero_bars()
    refresh_dungeon_map()


def refresh_dungeon_map():
    # Redessine la carte visuelle de progression (30 salles, mi-boss, boss final)
    if hero is None:
        return

    dungeon_map_canvas.delete("all")

    cols = 10
    margin_x, margin_y = 40, 25
    spacing_x, spacing_y = 95, 45
    radius = 14

    def node_pos(room_num):
        idx = room_num - 1
        r = idx // cols
        c = idx % cols
        if r % 2 == 1:
            c = cols - 1 - c
        return margin_x + c * spacing_x, margin_y + r * spacing_y

    # Lignes de connexion d'abord, pour qu'elles passent sous les pastilles
    for room_num in range(2, ROOMS_BEFORE_BOSS + 1):
        x1, y1 = node_pos(room_num - 1)
        x2, y2 = node_pos(room_num)
        dungeon_map_canvas.create_line(x1, y1, x2, y2, fill="#5c4033", width=2)

    for room_num in range(1, ROOMS_BEFORE_BOSS + 1):
        x, y = node_pos(room_num)

        if room_num == MIDBOSS_ROOM:
            outline, outline_w, label = "#32cd32", 3, "R"
        elif room_num == ROOMS_BEFORE_BOSS:
            outline, outline_w, label = "#ff4500", 3, "Z"
        else:
            outline, outline_w, label = "#5c4033", 2, str(room_num)

        if room_num < current_room:
            fill = "#4a7c59"
        elif room_num == current_room:
            fill = "gold"
        else:
            fill = "#2d1b0f"

        dungeon_map_canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, outline=outline, width=outline_w)
        text_color = "black" if fill == "gold" else "white"
        dungeon_map_canvas.create_text(x, y, text=label, fill=text_color, font=("Arial", 9, "bold"))


def generate_path_choices():
    # Affiche les 3 choix de chemin
    if hero is None or hero["pv"] <= 0:
        return

    frame_chemins.pack(pady=10)
    path_left_btn.config(text=f"🚪 {random.choice(phrases_left)}")
    path_mid_btn.config(text=f"🚪 {random.choice(phrases_middle)}")
    path_right_btn.config(text=f"🚪 {random.choice(phrases_right)}")


event_types = ["combat", "patrouille", "loot_chest", "empty_room", "trap_room", "taverne", "interaction", "marchand"]

# Poids d'événements selon la porte choisie : chaque chemin a sa propre personnalité
path_weights = {
    # Gauche : risque/récompense — plus de coffres et de pièges, moins de combats
    "left":   {"combat": 10, "patrouille": 10, "loot_chest": 26, "empty_room": 8, "trap_room": 20, "taverne": 8, "interaction": 12, "marchand": 6},
    # Milieu : la voie classique, équilibrée
    "middle": {"combat": 18, "patrouille": 15, "loot_chest": 13, "empty_room": 13, "trap_room": 11, "taverne": 11, "interaction": 11, "marchand": 8},
    # Droite : la voie prudente — plus de repos, d'interactions et de commerce, moins de danger
    "right":  {"combat": 9, "patrouille": 7, "loot_chest": 9, "empty_room": 19, "trap_room": 7, "taverne": 19, "interaction": 18, "marchand": 12},
}


def choose_path(direction="middle"):
    # Fait avancer le joueur dans une nouvelle salle
    # Le chemin choisi influence réellement les probabilités d'événement
    global current_room

    if hero is None:
        return

    frame_chemins.pack_forget()
    current_room += 1
    refresh_hero_display()

    if current_room >= ROOMS_BEFORE_BOSS:
        start_boss_combat_phase()
        return

    if current_room == MIDBOSS_ROOM:
        start_midboss_combat_phase()
        return

    weights_dict = path_weights.get(direction, path_weights["middle"])
    weights = [weights_dict[e] for e in event_types]
    event_roll = random.choices(event_types, weights=weights, k=1)[0]

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
    elif event_roll == "marchand":
        trigger_merchant_event()


def trigger_trap():
    # Gère une salle-piège, avec un jet de dé visuel avant résolution
    if hero is None:
        return

    total_dexterity = get_effective_stat("adresse")
    roll = random.randint(1, 25)
    success = roll < total_dexterity
    animate_dice_roll(roll, 25, success, lambda: resolve_trap(success))


def resolve_trap(success):
    if hero is None:
        return

    if success:
        log_feed.config(
            text=f"[Salle {current_room}] Un piège s'active ! Grâce à ton ADRESSE, tu l'esquives avec élégance.",
            fg="lightgreen"
        )
    else:
        dmg = apply_damage_to_hero(random.randint(6, 12))
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
             "- Boire une bière tiède douteuse (Coûte 10 pièces, rend toute ta Mana)\n"
             "- Ne rien faire et repartir",
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

    elif choix == "rien":
        log_feed.config(text="Tu jettes un œil méfiant autour de toi et repars sans rien consommer.", fg="white")

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


# --- MARCHAND ---
# État de l'offre du marchand courant (régénérée à chaque rencontre)
merchant_offer = {"armure": None, "casque": None, "bottes": None}


def trigger_merchant_event():
    # Rencontre d'un marchand : tire une pièce d'équipement en vente pour chaque emplacement
    if hero is None:
        return

    merchant_offer["armure"] = random.choice(armure_catalog)
    merchant_offer["casque"] = random.choice(casque_catalog)
    merchant_offer["bottes"] = random.choice(bottes_catalog)

    refresh_merchant_offer_labels()

    log_feed.config(
        text=f"🛒 [Salle {current_room}] Un marchand ambulant a monté son étal ici. 'Achète, vends, mais fais vite, mon gars !'\n"
             f"Tu as {hero['or']} pièces d'or.",
        fg="#daa520"
    )
    frame_marchand.pack(pady=10)


def refresh_merchant_offer_labels():
    # Met à jour le texte des boutons d'achat d'équipement selon l'offre du marchand
    for slot, btn in (("armure", buy_armure_btn), ("casque", buy_casque_btn), ("bottes", buy_bottes_btn)):
        item = merchant_offer[slot]
        if item:
            btn.config(text=f"{item['nom']} [{item['rare']}] +{item['def']} Déf — {item['prix']} or")


def buy_potion_from_merchant():
    buy_consumable("potion", 15)


def buy_food_from_merchant():
    buy_consumable("nourriture", 8)


def buy_mana_from_merchant():
    buy_consumable("mana", 12)


def buy_consumable(kind, prix):
    if hero is None:
        return
    if hero["or"] < prix:
        log_feed.config(text="Pas assez d'or pour ça.", fg="orange")
        return
    hero["or"] -= prix
    hero["consommables"][kind] = hero["consommables"].get(kind, 0) + 1
    labels = {"potion": "potion de soin", "nourriture": "ration de voyage", "mana": "fiole de mana"}
    label = labels.get(kind, kind)
    log_feed.config(text=f"Tu achètes une {label} pour {prix} or.", fg="lightgreen")
    refresh_hero_display()


def buy_equipment_from_merchant(slot):
    if hero is None:
        return
    item = merchant_offer.get(slot)
    if item is None:
        return
    if hero["or"] < item["prix"]:
        log_feed.config(text="Pas assez d'or pour cet équipement.", fg="orange")
        return

    hero["or"] -= item["prix"]
    new_item = item.copy()
    old_item = hero["equipement"].get(slot)
    hero["equipement"][slot] = new_item
    if old_item:
        hero["inventaire"].append(old_item)
        log_feed.config(text=f"Tu achètes {new_item['nom']} et l'enfiles ! ({old_item['nom']} rangée dans ton sac)", fg="lightgreen")
    else:
        log_feed.config(text=f"Tu achètes {new_item['nom']} et l'enfiles !", fg="lightgreen")

    refresh_hero_display()
    refresh_inventory_button()


def sell_item_value(item):
    # Estime le prix de rachat d'un objet (arme ou équipement) par le marchand
    if "dmg" in item:
        return max(3, item["dmg"] * 3 + item["stat_val"] * 4)
    return max(3, item.get("def", 0) * 4 + item.get("stat_val", 0) * 4)


def open_merchant_sell_window():
    # Fenêtre de vente : liste les objets du sac (hors objets équipés)
    if hero is None:
        return

    sell_win = tk.Toplevel(window)
    sell_win.title("🛒 Vendre au marchand")
    sell_win.configure(bg="#2d1b0f")
    sell_win.geometry("480x420")
    try:
        sell_win.transient(window)
    except tk.TclError:
        pass

    tk.Label(sell_win, text="🛒 VENDRE DES OBJETS", font=("Arial", 14, "bold"), bg="#2d1b0f", fg="gold").pack(pady=8)

    list_frame = tk.Frame(sell_win, bg="#2d1b0f")
    list_frame.pack(fill="both", expand=True, padx=10, pady=8)

    if not hero["inventaire"]:
        tk.Label(list_frame, text="Ton sac est vide, rien à vendre.", bg="#2d1b0f", fg="white").pack(pady=10)
    else:
        for idx, w in enumerate(hero["inventaire"]):
            row = tk.Frame(list_frame, bg="#3e2a17")
            row.pack(fill="x", pady=3)
            prix = sell_item_value(w)
            tk.Label(
                row, text=f"{item_display_info(w)} — {prix} or", bg="#3e2a17", fg="white",
                anchor="w", justify="left", wraplength=320
            ).pack(side="left", padx=6, fill="x", expand=True)
            tk.Button(
                row, text="Vendre", bg="#daa520", fg="black",
                command=lambda i=idx: sell_item_from_inventory(i, sell_win)
            ).pack(side="left", padx=3)

    tk.Button(sell_win, text="Fermer", bg="#20b2aa", fg="white", command=sell_win.destroy).pack(pady=10)


def sell_item_from_inventory(index, win=None):
    if hero is None or index >= len(hero["inventaire"]):
        return

    item = hero["inventaire"].pop(index)
    prix = sell_item_value(item)
    add_gold(prix)

    refresh_hero_display()
    refresh_inventory_button()
    log_feed.config(text=f"Tu vends {item['nom']} pour {prix} or.", fg="lightgreen")

    if win is not None:
        win.destroy()
        open_merchant_sell_window()


def leave_merchant():
    frame_marchand.pack_forget()
    if hero is not None and hero["pv"] > 0:
        generate_path_choices()


def generate_chest_loot():
    # Tente d'ouvrir un coffre : un jet d'ADRESSE visuel détermine si l'ouverture est propre
    # ou si un mécanisme piégé se déclenche avant de récupérer le butin.
    if hero is None:
        return

    total_dexterity = get_effective_stat("adresse")
    roll = random.randint(1, 20)
    success = roll <= total_dexterity
    animate_dice_roll(roll, 20, success, lambda: resolve_chest_loot(success))


def resolve_chest_loot(chest_success):
    # Génère une arme OU une pièce d'équipement dans un coffre, avec pénalité si l'ouverture a échoué
    if hero is None:
        return

    log_prefix = ""
    if not chest_success:
        raw_dmg = random.randint(4, 8)
        real_dmg = apply_damage_to_hero(raw_dmg)
        log_prefix = f"⚠️ Un mécanisme piégé se déclenche en forçant la serrure ! Tu perds {real_dmg} PV.\n\n"
        refresh_hero_display()
        evaluate_death_state()
        if hero["pv"] <= 0:
            return

    rarity_roll = random.randint(1, 100)
    if not chest_success:
        # Une ouverture ratée abîme un peu le contenu : pas de coup de chance légendaire
        rarity_roll = min(rarity_roll, 60)

    if random.random() < 0.6:
        # --- Loot d'arme ---
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
        hero["loot_item"] = {"nom": nom_w, "rare": tier, "dmg": dmg, "stat": stat, "stat_val": buff}

        arme_actuelle = hero["arme"]
        diff_dmg = dmg - arme_actuelle["dmg"]
        diff_txt = f"+{diff_dmg}" if diff_dmg >= 0 else str(diff_dmg)

        log = (
            f"{log_prefix}"
            f"📦 [Salle {current_room}] COFFRE TRÉSOR !\n"
            f"Un coffre en bois vermoulu t'attend.\n"
            f"Trouvé : {nom_w} [{tier}]\n"
            f"Stats : +{dmg} Dégâts | +{buff} {stat.upper()}\n"
            f"🔄 Comparé à ton arme actuelle ({arme_actuelle['nom']}, +{arme_actuelle['dmg']} Dégâts) : {diff_txt} Dégâts"
        )
    else:
        # --- Loot d'équipement (armure / casque / bottes) ---
        slot = random.choice(["armure", "casque", "bottes"])
        equip_prefix = {
            "armure": ["Cuirasse", "Plastron", "Gilet", "Cape rembourrée"],
            "casque": ["Casque", "Heaume", "Bonnet", "Capuche"],
            "bottes": ["Bottes", "Sandales", "Chaussures", "Bottines"]
        }
        if rarity_roll > 90:
            tier = "Légendaire"
            suffix = random.choice(suffix_legendary)
            defense = random.randint(6, 9)
            buff = random.randint(3, 5)
            color = "#ff4500"
        elif rarity_roll > 60:
            tier = "Rare"
            suffix = random.choice(suffix_rare)
            defense = random.randint(3, 5)
            buff = random.randint(1, 3)
            color = "#1e90ff"
        else:
            tier = "Commun"
            suffix = random.choice(suffix_common)
            defense = random.randint(1, 2)
            buff = random.randint(0, 1)
            color = "white"

        nom_e = f"{random.choice(equip_prefix[slot])} {suffix}"
        stat = random.choice(["force", "intelligence", "adresse", "courage"])
        hero["loot_item"] = {"nom": nom_e, "rare": tier, "def": defense, "stat": stat, "stat_val": buff, "slot": slot}

        piece_actuelle = hero["equipement"].get(slot)
        def_actuelle = piece_actuelle["def"] if piece_actuelle else 0
        diff_def = defense - def_actuelle
        diff_txt = f"+{diff_def}" if diff_def >= 0 else str(diff_def)
        nom_actuel = piece_actuelle["nom"] if piece_actuelle else "aucune pièce"

        log = (
            f"{log_prefix}"
            f"📦 [Salle {current_room}] COFFRE TRÉSOR !\n"
            f"Un coffre en bois vermoulu t'attend.\n"
            f"Trouvé : {nom_e} [{tier}] ({slot.upper()})\n"
            f"Stats : +{defense} Défense | +{buff} {stat.upper()}\n"
            f"🔄 Comparé à ta pièce actuelle ({nom_actuel}) : {diff_txt} Défense"
        )

    log_feed.config(text=log, fg=color)
    loot_frame.pack(pady=10)


def accept_loot_item():
    # Équipe l'objet trouvé (arme ou équipement) ; l'ancien objet rejoint l'inventaire au lieu d'être perdu
    if hero is None or hero.get("loot_item") is None:
        log_feed.config(text="Rien à équiper.", fg="orange")
        loot_frame.pack_forget()
        return

    item = hero["loot_item"]
    hero["loot_item"] = None

    if "dmg" in item:
        old_item = hero["arme"]
        hero["arme"] = item
        hero["inventaire"].append(old_item)
        msg = f"Tu as équipé avec fierté : {item['nom']} ! ({old_item['nom']} rangée dans ton sac)"
    else:
        slot = item["slot"]
        old_item = hero["equipement"].get(slot)
        hero["equipement"][slot] = item
        if old_item:
            hero["inventaire"].append(old_item)
            msg = f"Tu enfiles {item['nom']} ! ({old_item['nom']} rangée dans ton sac)"
        else:
            msg = f"Tu enfiles {item['nom']} !"

    log_feed.config(text=msg, fg="lightgreen")
    loot_frame.pack_forget()
    refresh_hero_display()
    refresh_inventory_button()
    generate_path_choices()


def store_loot_item():
    # Range l'objet trouvé dans l'inventaire sans l'équiper
    if hero is None or hero.get("loot_item") is None:
        loot_frame.pack_forget()
        return

    item = hero["loot_item"]
    hero["inventaire"].append(item)
    log_feed.config(text=f"Tu ranges {item['nom']} dans ton sac.", fg="yellow")
    hero["loot_item"] = None
    loot_frame.pack_forget()
    refresh_inventory_button()
    generate_path_choices()


def discard_loot_item():
    # Ignore l'objet du coffre
    if hero is not None:
        hero["loot_item"] = None

    log_feed.config(text="Tu laisses l'objet dans le coffre.", fg="yellow")
    loot_frame.pack_forget()
    generate_path_choices()


# --- INVENTAIRE ---

def refresh_inventory_button():
    # Met à jour le compteur affiché sur le bouton inventaire
    if hero is None:
        return
    inv_btn.config(text=f"🎒 Inventaire ({len(hero['inventaire'])})")


def item_display_info(item):
    # Description courte d'un objet, qu'il s'agisse d'une arme ou d'une pièce d'équipement
    if "dmg" in item:
        return f"{item['nom']} [{item['rare']}] ⚔️ Arme | +{item['dmg']} Dégâts | +{item['stat_val']} {item['stat'].upper()}"
    return f"{item['nom']} [{item['rare']}] 🛡️ {item['slot'].capitalize()} | +{item.get('def', 0)} Défense | +{item.get('stat_val', 0)} {item['stat'].upper()}"


def use_potion():
    # Utilise une potion de soin (disponible en combat comme hors combat)
    if hero is None:
        return
    if hero["consommables"].get("potion", 0) <= 0:
        log_feed.config(text="Tu n'as plus de potion de soin.", fg="orange")
        return

    hero["consommables"]["potion"] -= 1
    heal = 30
    hero["pv"] = min(hero["pv_max"], hero["pv"] + heal)
    msg = f"🧪 Tu bois une potion de soin. +{heal} PV !"

    if current_monster is not None:
        msg += execute_enemy_counter()

    refresh_hero_display()
    refresh_inventory_button()
    log_feed.config(text=msg, fg="lightgreen")


def use_food():
    # Utilise une ration de nourriture (disponible en combat comme hors combat)
    if hero is None:
        return
    if hero["consommables"].get("nourriture", 0) <= 0:
        log_feed.config(text="Tu n'as plus de ration de voyage.", fg="orange")
        return

    hero["consommables"]["nourriture"] -= 1
    heal_pv = 15
    heal_mana = 8
    hero["pv"] = min(hero["pv_max"], hero["pv"] + heal_pv)
    hero["mana"] = min(hero["mana_max"], hero["mana"] + heal_mana)
    msg = f"🍖 Tu grignotes une ration de voyage. +{heal_pv} PV / +{heal_mana} Mana !"

    if current_monster is not None:
        msg += execute_enemy_counter()

    refresh_hero_display()
    refresh_inventory_button()
    log_feed.config(text=msg, fg="lightgreen")


def use_mana_potion():
    # Utilise une fiole de mana (disponible en combat comme hors combat)
    if hero is None:
        return
    if hero["consommables"].get("mana", 0) <= 0:
        log_feed.config(text="Tu n'as plus de fiole de mana.", fg="orange")
        return

    hero["consommables"]["mana"] -= 1
    restore = 20
    hero["mana"] = min(hero["mana_max"], hero["mana"] + restore)
    msg = f"🔮 Tu bois une fiole de mana. +{restore} Mana !"

    if current_monster is not None:
        msg += execute_enemy_counter()

    refresh_hero_display()
    refresh_inventory_button()
    log_feed.config(text=msg, fg="lightgreen")


def open_inventory():
    # Affiche une fenêtre listant l'équipement porté, les objets en réserve et les consommables
    if hero is None:
        return

    inv_win = tk.Toplevel(window)
    inv_win.title("🎒 Inventaire")
    inv_win.configure(bg="#2d1b0f")
    inv_win.geometry("520x560")
    try:
        inv_win.transient(window)
    except tk.TclError:
        pass

    tk.Label(inv_win, text="🎒 INVENTAIRE", font=("Arial", 14, "bold"), bg="#2d1b0f", fg="gold").pack(pady=8)

    equipped = hero["arme"]
    equip = hero["equipement"]
    equipped_txt = f"⚔️ Arme : {equipped['nom']} [{equipped['rare']}] | +{equipped['dmg']} Dégâts | +{equipped['stat_val']} {equipped['stat'].upper()}\n"
    for slot, icon, label in (("armure", "🥋", "Armure"), ("casque", "⛑️", "Casque"), ("bottes", "🥾", "Bottes")):
        piece = equip.get(slot)
        if piece:
            equipped_txt += f"{icon} {label} : {piece['nom']} [{piece['rare']}] | +{piece['def']} Défense | +{piece['stat_val']} {piece['stat'].upper()}\n"
        else:
            equipped_txt += f"{icon} {label} : -- aucune --\n"

    tk.Label(
        inv_win, text=equipped_txt.strip(), font=("Arial", 10, "bold"), bg="#2d1b0f", fg="lightgreen",
        wraplength=480, justify="left"
    ).pack(pady=4, padx=10)

    conso = hero["consommables"]
    conso_frame = tk.Frame(inv_win, bg="#2d1b0f")
    conso_frame.pack(pady=6)
    tk.Label(conso_frame, text=f"🧪 Potions de soin : {conso.get('potion', 0)}", bg="#2d1b0f", fg="white").pack(side="left", padx=6)
    tk.Button(conso_frame, text="Utiliser", bg="#4a7c59", fg="white", command=lambda: (use_potion(), refresh_open_inventory(inv_win))).pack(side="left", padx=4)
    tk.Label(conso_frame, text=f"🍖 Rations : {conso.get('nourriture', 0)}", bg="#2d1b0f", fg="white").pack(side="left", padx=10)
    tk.Button(conso_frame, text="Utiliser", bg="#4a7c59", fg="white", command=lambda: (use_food(), refresh_open_inventory(inv_win))).pack(side="left", padx=4)
    tk.Label(conso_frame, text=f"🔮 Mana : {conso.get('mana', 0)}", bg="#2d1b0f", fg="white").pack(side="left", padx=10)
    tk.Button(conso_frame, text="Utiliser", bg="#4a7c59", fg="white", command=lambda: (use_mana_potion(), refresh_open_inventory(inv_win))).pack(side="left", padx=4)

    tk.Label(inv_win, text="🧳 Sac (armes & équipement de réserve)", font=("Arial", 10, "bold"), bg="#2d1b0f", fg="gold").pack(pady=(8, 2))

    canvas_wrap = tk.Frame(inv_win, bg="#2d1b0f")
    canvas_wrap.pack(fill="both", expand=True, padx=10, pady=4)

    if not hero["inventaire"]:
        tk.Label(canvas_wrap, text="Ton sac est vide pour l'instant.", bg="#2d1b0f", fg="white").pack(pady=10)
    else:
        for idx, w in enumerate(hero["inventaire"]):
            row = tk.Frame(canvas_wrap, bg="#3e2a17")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=item_display_info(w), bg="#3e2a17", fg="white", anchor="w", justify="left", wraplength=300).pack(
                side="left", padx=6, fill="x", expand=True
            )
            tk.Button(
                row, text="Équiper", bg="#4a7c59", fg="white",
                command=lambda i=idx: equip_from_inventory(i, inv_win)
            ).pack(side="left", padx=3)
            tk.Button(
                row, text="Jeter", bg="#8b0000", fg="white",
                command=lambda i=idx: discard_from_inventory(i, inv_win)
            ).pack(side="left", padx=3)

    tk.Button(inv_win, text="Fermer", bg="#20b2aa", fg="white", command=inv_win.destroy).pack(pady=10)


def refresh_open_inventory(win):
    # Rafraîchit la fenêtre d'inventaire ouverte (après usage d'un consommable par ex.)
    try:
        win.destroy()
    except tk.TclError:
        pass
    open_inventory()


def equip_from_inventory(index, win=None):
    # Équipe l'objet choisi dans le sac (arme ou équipement), l'ancien objet revient dans le sac
    if hero is None or index >= len(hero["inventaire"]):
        return

    item = hero["inventaire"].pop(index)

    if "dmg" in item:
        old_item = hero["arme"]
        hero["arme"] = item
    else:
        slot = item["slot"]
        old_item = hero["equipement"].get(slot)
        hero["equipement"][slot] = item

    hero["inventaire"].append(old_item)

    refresh_hero_display()
    refresh_inventory_button()
    log_feed.config(text=f"Tu équipes {item['nom']} !", fg="lightgreen")

    if win is not None:
        win.destroy()
        open_inventory()


def discard_from_inventory(index, win=None):
    # Jette définitivement un objet du sac
    if hero is None or index >= len(hero["inventaire"]):
        return

    removed = hero["inventaire"].pop(index)
    refresh_inventory_button()
    log_feed.config(text=f"Tu jettes {removed['nom']}.", fg="yellow")

    if win is not None:
        win.destroy()
        open_inventory()


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
    # Lance le jet de dé visuel correspondant au choix fait pendant la patrouille
    if hero is None:
        return

    frame_evenement.pack_forget()

    if option == "discret":
        stat_eff = get_effective_stat("adresse")
        roll = random.randint(1, 20)
        success = roll <= stat_eff
        animate_dice_roll(roll, 20, success, lambda: resolve_patrol_event("discret", success))

    elif option == "baston":
        stat_eff = get_effective_stat("courage")
        roll = random.randint(1, 20)
        success = roll <= stat_eff
        animate_dice_roll(roll, 20, success, lambda: resolve_patrol_event("baston", success))


def resolve_patrol_event(option, success):
    if hero is None:
        return

    if option == "discret":
        if success:
            hero["xp"] += 20
            log_feed.config(text=f"Incroyable, {hero['nom']} n'a fait aucun bruit. Vous passez inaperçus ! (+20 XP)", fg="lightgreen")
        else:
            degats = apply_damage_to_hero(random.randint(10, 15))
            log_feed.config(
                text=f"{hero['nom']} trébuche sur un tabouret. Les gardes vous repèrent avant de sonner l'alarme ! (-{degats} PV)",
                fg="red"
            )
            evaluate_death_state()

    elif option == "baston":
        if success:
            butin = random.randint(15, 30)
            add_gold(butin)
            log_feed.config(text=f"Votre folie furieuse les terrorise ! Ils lâchent leur bourse et détalent. (+{butin} pièces)", fg="lightgreen")
        else:
            degats = apply_damage_to_hero(random.randint(8, 12))
            log_feed.config(
                text=f"La charge rate lamentablement. Vous prenez quelques coups avant de les semer. (-{degats} PV)",
                fg="red"
            )
            evaluate_death_state()

    refresh_hero_display()
    if hero["pv"] > 0:
        generate_path_choices()


# --- SYSTÈME DE COMBAT ---

def get_difficulty_scale():
    # Multiplicateur de force/PV des monstres selon la difficulté choisie par le héros
    if hero is None:
        return 1.0
    return DIFFICULTY_SCALING.get(hero.get("difficulte", "Normal"), 1.0)


def start_combat_phase():
    # Lance un combat classique, avec une difficulté qui augmente selon la salle atteinte et le mode choisi
    global current_monster
    current_monster = random.choice(monsters_pool).copy()
    current_monster["boss"] = False
    play_combat_music()

    # Scaling progressif : +3% de force/PV par salle passée (jusqu'à ~+85% en fin de donjon), modulé par la difficulté
    scale = (1 + (current_room - 1) * 0.03) * get_difficulty_scale()
    current_monster["force"] = max(1, int(current_monster["force"] * scale))
    current_monster["pv"] = max(1, int(current_monster["pv"] * scale))
    current_monster["pv_max"] = current_monster["pv"]

    log_feed.config(
        text=f"💥 [Salle {current_room}] ALERTE BASTON ! {current_monster['nom']} charge ! (PV: {current_monster['pv']})",
        fg="red"
    )
    monster_bar_canvas.pack(pady=4)
    refresh_monster_bar()
    combat_frame.pack(pady=10)


def start_midboss_combat_phase():
    # Lance le combat du mi-boss (salle 15) : Reivax, le second de Zangdar
    global current_monster
    play_combat_music()
    diff_scale = get_difficulty_scale()
    base_force, base_pv = 13, 45
    current_monster = {
        "nom": "Reivax",
        "force": max(1, int(base_force * diff_scale)),
        "pv": max(1, int(base_pv * diff_scale)),
        "pv_max": max(1, int(base_pv * diff_scale)),
        "xp": 150,
        "boss": True,
        "final_boss": False,
        "enrage": False,
        "spells": boss_spells_reivax,
        "enrage_spell": _reivax_traitrise,
    }
    log_feed.config(
        text=f"🟢 [SALLE {MIDBOSS_ROOM} - MI-PARCOURS] 'Héhéhé... Zangdar m'a chargé de vous arrêter ici, brêles !'\n"
             f"{current_monster['nom']} le gobelin sournois, second de Zangdar, surgit de l'ombre ! (PV: {current_monster['pv']})",
        fg="#32cd32"
    )
    monster_bar_canvas.pack(pady=4)
    refresh_monster_bar()
    combat_frame.pack(pady=10)


def start_boss_combat_phase():
    # Lance le combat du boss final
    global current_monster
    play_combat_music()
    diff_scale = get_difficulty_scale()
    base_force, base_pv = 16, 65
    current_monster = {
        "nom": "Zangdar (BOSS FINAL)",
        "force": max(1, int(base_force * diff_scale)),
        "pv": max(1, int(base_pv * diff_scale)),
        "pv_max": max(1, int(base_pv * diff_scale)),
        "xp": 500,
        "boss": True,
        "final_boss": True,
        "enrage": False,
        "spells": boss_spells_zangdar,
        "enrage_spell": _boss_rage_administrative,
    }
    log_feed.config(
        text=f"👿 [SALLE {ROOMS_BEFORE_BOSS} - BOSS] 'Par les sbires de l'enfer ! Qui foule le tapis de mon bureau ?!'\n"
             f"Le terrible {current_monster['nom']} vous attaque ! (PV: {current_monster['pv']})",
        fg="gold"
    )
    monster_bar_canvas.pack(pady=4)
    refresh_monster_bar()
    combat_frame.pack(pady=10)


def execute_enemy_counter():
    # Fait attaquer le monstre après l'action du héros
    if hero is None or current_monster is None:
        return ""

    if current_monster["pv"] <= 0:
        return ""

    if current_monster.get("boss"):
        return execute_boss_attack()

    f_totale = get_effective_stat("force")
    dmg_raw = max(1, (random.randint(2, 6) + (current_monster["force"] // 3)) - (f_totale // 6))
    dmg_m = apply_damage_to_hero(dmg_raw)
    refresh_hero_display()
    evaluate_death_state()
    return f"\nLe monstre riposte et t'inflige {dmg_m} dégâts !"


# --- SORTS DU BOSS ---
# Chaque sort est un dict : nom, texte, et une fonction qui applique l'effet et renvoie le message

def _boss_coup_de_tampon():
    f_totale = get_effective_stat("force")
    dmg_raw = max(1, (random.randint(6, 12) + (current_monster["force"] // 3)) - (f_totale // 6))
    dmg = apply_damage_to_hero(dmg_raw)
    return f"\n🗂️ Zangdar t'assène un Coup de Tampon Encreur ! (-{dmg} PV)"


def _boss_note_de_service():
    dmg = apply_damage_to_hero(random.randint(10, 16))
    return f"\n📋 'Ceci est une Note de Service !' Zangdar te frappe avec un dossier épais. (-{dmg} PV)"


def _boss_reunion_interminable():
    perte = min(hero["mana"], random.randint(8, 14))
    hero["mana"] -= perte
    if perte > 0:
        return f"\n😴 Zangdar te convoque à une Réunion Interminable. Ton esprit s'épuise ! (-{perte} Mana)"
    return "\n😴 Zangdar tente de te convoquer en réunion, mais tu n'as plus rien à perdre."


def _boss_pause_cafe():
    heal = random.randint(6, 12)
    current_monster["pv"] = min(current_monster["pv_max"], current_monster["pv"] + heal)
    return f"\n☕ Zangdar prend une Pause Café administrative et récupère {heal} PV."


def _boss_rage_administrative():
    f_totale = get_effective_stat("force")
    dmg_raw = max(1, (random.randint(14, 20) + (current_monster["force"] // 2)) - (f_totale // 6))
    dmg = apply_damage_to_hero(dmg_raw)
    return f"\n🔥 RAGE ADMINISTRATIVE ! Zangdar hurle des articles de règlement et frappe très fort ! (-{dmg} PV)"


boss_spells_zangdar = [
    _boss_coup_de_tampon,
    _boss_coup_de_tampon,
    _boss_note_de_service,
    _boss_reunion_interminable,
    _boss_pause_cafe,
]


# --- SORTS DE REIVAX (mi-boss, salle 15) ---

def _reivax_coup_bas():
    dmg = apply_damage_to_hero(random.randint(8, 14))
    return f"\n🔪 Reivax vise bas et te frappe sournoisement ! (-{dmg} PV)"


def _reivax_fumigene():
    perte = min(hero["mana"], random.randint(6, 10))
    hero["mana"] -= perte
    if perte > 0:
        return f"\n💨 Reivax balance une Fumigène Puante, tu suffoques ! (-{perte} Mana)"
    return "\n💨 Reivax balance une fumigène, mais tu as déjà l'habitude de l'odeur."


def _reivax_planque():
    heal = random.randint(4, 8)
    current_monster["pv"] = min(current_monster["pv_max"], current_monster["pv"] + heal)
    return f"\n🕶️ Reivax se planque dans l'ombre et panse ses plaies. (+{heal} PV)"


def _reivax_traitrise():
    f_totale = get_effective_stat("force")
    dmg_raw = max(1, (random.randint(12, 18) + (current_monster["force"] // 2)) - (f_totale // 6))
    dmg = apply_damage_to_hero(dmg_raw)
    return f"\n🗡️ TRAHISON ! Reivax profite d'une ouverture pour un coup fourbe et brutal ! (-{dmg} PV)"


boss_spells_reivax = [
    _reivax_coup_bas,
    _reivax_coup_bas,
    _reivax_fumigene,
    _reivax_planque,
]


def execute_boss_attack():
    # Le boss (Reivax ou Zangdar) choisit une action parmi ses sorts propres,
    # avec une phase d'enrage sous 40% de PV qui débloque un sort plus puissant
    if hero is None or current_monster is None:
        return ""

    msg = ""

    if not current_monster.get("enrage") and current_monster["pv"] <= current_monster["pv_max"] * 0.4:
        current_monster["enrage"] = True
        current_monster["force"] += 6
        msg += f"\n\n👿 {current_monster['nom']} entre dans une rage folle ! Il devient bien plus dangereux !"

    spell_pool = list(current_monster.get("spells", []))
    if current_monster.get("enrage") and current_monster.get("enrage_spell"):
        spell_pool.append(current_monster["enrage_spell"])

    spell = random.choice(spell_pool) if spell_pool else _boss_coup_de_tampon
    msg += spell()

    refresh_hero_display()
    refresh_monster_bar()
    evaluate_death_state()
    return msg


def check_level_up():
    # Gère la montée de niveau du héros
    if hero is None:
        return ""

    msg_lvl = ""

    while hero["xp"] >= hero["xp_requis"]:
        hero["niveau"] += 1
        hero["xp"] -= hero["xp_requis"]
        hero["xp_requis"] = int(hero["xp_requis"] * 1.35)
        hero["pv_max"] += 10
        hero["mana_max"] += 5
        hero["pv"] = hero["pv_max"]
        hero["mana"] = hero["mana_max"]
        msg_lvl += " 🎉 NIVEAU SUPÉRIEUR !"

        if hero["niveau"] >= 2:
            refresh_skill_buttons()

    return msg_lvl


def check_victory():
    # Vérifie si le monstre est mort
    global current_monster

    if hero is None or current_monster is None:
        return False

    if current_monster["pv"] <= 0:
        monster_bar_canvas.pack_forget()
        combat_frame.pack_forget()
        hero["stats"]["monstres_tues"] += 1

        if current_monster.get("final_boss"):
            gains_or = random.randint(100, 200)
        elif current_monster.get("boss"):
            gains_or = random.randint(40, 70)
        else:
            gains_or = random.randint(5, 15)

        add_gold(gains_or)
        hero["xp"] += current_monster["xp"]

        msg_lvl = check_level_up()
        refresh_hero_display()

        if current_monster.get("final_boss"):
            trigger_final_victory()
            current_monster = None
            return True

        if current_monster.get("boss"):
            play_ambient_music()
            log_feed.config(
                text=f"🎉 Reivax s'effondre en couinant ! 'Zangdar... me... vengera...'\n"
                     f"Tu récupères {gains_or} pièces et {current_monster['xp']} XP.{msg_lvl}",
                fg="gold"
            )
            current_monster = None
            generate_path_choices()
            return True

        play_ambient_music()
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

    f_totale = get_effective_stat("force")
    dmg_h = random.randint(3, 7) + (f_totale // 4) + hero["arme"]["dmg"]
    current_monster["pv"] -= dmg_h
    refresh_monster_bar()

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
        is_crit = random.randint(1, 5) == 1
        dmg = (28 + w_dmg) if is_crit else (10 + w_dmg // 2)
        current_monster["pv"] -= dmg
        log += f"{'💥 COUP CRITIQUE ! ' if is_crit else ''}{dmg} dégâts perfides."
        dealt_damage = True

    elif skill_name == "Lame Toxique":
        is_crit = random.randint(1, 5) == 1
        dmg = (28 + w_dmg) if is_crit else (10 + w_dmg // 2)
        current_monster["pv"] -= dmg
        log += f"{'☠️ POISON VIRULENT ! ' if is_crit else ''}{dmg} dégâts empoisonnés."
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
    refresh_monster_bar()

    if dealt_damage and check_victory():
        return

    log += execute_enemy_counter()
    refresh_hero_display()

    if hero["pv"] > 0 and current_monster is not None:
        log_feed.config(text=f"{log}\n({current_monster['nom']} PV: {current_monster['pv']})", fg="violet")


def execute_flee_action():
    # Tente de fuir un combat, avec un jet de dé visuel (sauf face au boss final)
    global current_monster

    if hero is None or current_monster is None:
        log_feed.config(text="Aucun combat en cours.", fg="orange")
        return

    if current_monster.get("final_boss"):
        log_feed.config(text="Impossible de fuir face au boss final. Ce serait trop facile.", fg="orange")
        return

    flee_stat = get_effective_stat("adresse")
    roll = random.randint(1, 20)
    success = roll <= flee_stat
    animate_dice_roll(roll, 20, success, lambda: resolve_flee(success))


def resolve_flee(success):
    global current_monster

    if hero is None or current_monster is None:
        return

    if success:
        monster_bar_canvas.pack_forget()
        combat_frame.pack_forget()
        play_ambient_music()
        log_feed.config(text="🏃 Tu prends tes jambes à ton cou et disparais dans le couloir !", fg="lightgreen")
        current_monster = None
        generate_path_choices()
    else:
        log = "🏃 Tu tentes de fuir, mais tu glisses sur un truc visqueux."
        log += execute_enemy_counter()
        if hero["pv"] > 0 and current_monster is not None:
            log_feed.config(text=log, fg="orange")


# --- FIN DE PARTIE ---

def format_duration(seconds):
    # Formate une durée en secondes en "X min YY s"
    seconds = max(0, int(seconds))
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes} min {secs:02d} s"


def build_run_summary():
    # Construit le texte récapitulatif affiché à la fin d'une partie (victoire ou défaite)
    if hero is None:
        return ""
    stats = hero.get("stats", {})
    elapsed = time.time() - stats.get("temps_debut", time.time())
    return (
        f"\n\n📊 RÉSUMÉ DE LA PARTIE\n"
        f"👹 Monstres vaincus : {stats.get('monstres_tues', 0)}\n"
        f"🪙 Or amassé au total : {stats.get('or_gagne', 0)} pièces\n"
        f"🏰 Salles parcourues : {current_room}/{ROOMS_BEFORE_BOSS}\n"
        f"⏱️ Temps de jeu : {format_duration(elapsed)}\n"
        f"🎚️ Difficulté : {hero.get('difficulte', 'Normal')}"
    )


def trigger_final_victory():
    # Affiche la victoire finale avec image si disponible
    global victory_image_ref

    monster_bar_canvas.pack_forget()
    combat_frame.pack_forget()
    loot_frame.pack_forget()
    frame_chemins.pack_forget()
    frame_taverne.pack_forget()
    frame_evenement.pack_forget()
    frame_marchand.pack_forget()
    stop_music()

    image_ok = show_end_image(victory_image_ref)
    summary = build_run_summary()

    if image_ok:
        log_feed.config(
            text=f"🎉 VICTOIRE HISTORIQUE ! Tu as terrassé Zangdar et récupéré la douzième statuette de Gladeulfeurha !{summary}",
            fg="gold"
        )
    else:
        img_path = os.path.join(SCRIPT_DIR, "victoire.png")
        detail = image_load_errors.get("victoire.png")
        detail_txt = f"\nDétail de l'erreur : {detail}" if detail else ""
        log_feed.config(
            text=f"🎉 VICTOIRE ! Image impossible à afficher.\nChemin testé : {img_path}{detail_txt}{summary}",
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

        monster_bar_canvas.pack_forget()
        combat_frame.pack_forget()
        loot_frame.pack_forget()
        frame_chemins.pack_forget()
        frame_taverne.pack_forget()
        frame_evenement.pack_forget()
        frame_marchand.pack_forget()
        stop_music()

        image_ok = show_end_image(gameover_image_ref)
        summary = build_run_summary()

        if image_ok:
            log_feed.config(
                text=f"💀 Tu as succombé à la salle {current_room}. Fin de la compagnie. GAME OVER.{summary}",
                fg="red"
            )
        else:
            img_path = os.path.join(SCRIPT_DIR, "gameover.png")
            detail = image_load_errors.get("gameover.png")
            detail_txt = f"\nDétail de l'erreur : {detail}" if detail else ""
            log_feed.config(
                text=f"💀 GAME OVER ! Image impossible à afficher.\nChemin testé : {img_path}{detail_txt}{summary}",
                fg="red"
            )

        reset_btn.pack(pady=10)


def has_save_file(slot):
    return os.path.exists(get_save_path(slot))


def read_save_summary(slot):
    # Renvoie un résumé court du contenu d'un emplacement, ou None s'il est vide/invalide
    path = get_save_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        h = data.get("hero", {})
        return f"{h.get('nom', '?')} — Niveau {h.get('niveau', '?')} — Salle {data.get('current_room', '?')}/{ROOMS_BEFORE_BOSS}"
    except (OSError, json.JSONDecodeError, AttributeError):
        return None


def refresh_load_button_state():
    # Active/désactive le bouton "Charger" du menu selon la présence d'au moins une sauvegarde
    if any(has_save_file(s) for s in range(1, SAVE_SLOTS + 1)):
        load_btn.config(state="normal", bg="#4682b4")
    else:
        load_btn.config(state="disabled", bg="grey")


def save_game_to_slot(slot):
    # Sauvegarde la partie en cours dans l'emplacement choisi (hors combat uniquement)
    if hero is None:
        log_feed.config(text="Aucune partie en cours à sauvegarder.", fg="orange")
        return

    if current_monster is not None:
        log_feed.config(text="💾 Impossible de sauvegarder en plein combat ! Termine-le d'abord.", fg="orange")
        return

    data = {"hero": hero, "current_room": current_room}
    try:
        with open(get_save_path(slot), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log_feed.config(text=f"💾 Partie sauvegardée dans l'emplacement {slot} ! (Salle {current_room}/{ROOMS_BEFORE_BOSS})", fg="lightgreen")
    except OSError as e:
        log_feed.config(text=f"Erreur lors de la sauvegarde : {e}", fg="red")


def open_save_dialog():
    # Fenêtre de choix de l'emplacement où sauvegarder
    if hero is None:
        log_feed.config(text="Aucune partie en cours à sauvegarder.", fg="orange")
        return

    win = tk.Toplevel(window)
    win.title("💾 Sauvegarder")
    win.configure(bg="#2d1b0f")
    win.geometry("440x260")
    try:
        win.transient(window)
    except tk.TclError:
        pass

    tk.Label(win, text="💾 CHOISIR UN EMPLACEMENT", font=("Arial", 13, "bold"), bg="#2d1b0f", fg="gold").pack(pady=8)

    for slot in range(1, SAVE_SLOTS + 1):
        summary = read_save_summary(slot) or "-- emplacement vide --"
        row = tk.Frame(win, bg="#3e2a17")
        row.pack(fill="x", padx=10, pady=4)
        tk.Label(
            row, text=f"Emplacement {slot} : {summary}", bg="#3e2a17", fg="white",
            anchor="w", wraplength=280, justify="left"
        ).pack(side="left", padx=6, fill="x", expand=True)
        tk.Button(
            row, text="Sauvegarder", bg="#2e8b57", fg="white",
            command=lambda s=slot: (save_game_to_slot(s), win.destroy())
        ).pack(side="left", padx=4)

    tk.Button(win, text="Annuler", bg="#666666", fg="white", command=win.destroy).pack(pady=10)


def load_game_from_slot(slot):
    # Recharge une partie sauvegardée depuis l'emplacement choisi et reprend directement le donjon
    global hero, current_room, current_monster

    path = get_save_path(slot)
    if not os.path.exists(path):
        log_feed.config(text=f"L'emplacement {slot} est vide.", fg="orange")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log_feed.config(text=f"Erreur lors du chargement : {e}", fg="red")
        return

    loaded_hero = data.get("hero")
    if not loaded_hero:
        log_feed.config(text="Fichier de sauvegarde invalide.", fg="red")
        return

    # Compatibilité : s'assure que les clés ajoutées après coup existent toujours
    loaded_hero.setdefault("inventaire", [])
    loaded_hero.setdefault("loot_item", None)
    loaded_hero.setdefault("equipement", {"armure": None, "casque": None, "bottes": None})
    loaded_hero.setdefault("consommables", {"potion": 0, "nourriture": 0, "mana": 0})
    loaded_hero["consommables"].setdefault("mana", 0)
    loaded_hero.setdefault("difficulte", "Normal")
    loaded_hero.setdefault("stats", {"monstres_tues": 0, "or_gagne": loaded_hero.get("or", 0), "temps_debut": time.time()})
    loaded_hero["stats"].setdefault("temps_debut", time.time())

    hero = loaded_hero
    current_room = data.get("current_room", 0)
    current_monster = None

    frame_menu_creation.pack_forget()
    status_label.pack(fill="x", padx=40, pady=5)
    hero_display_frame.pack(pady=4)
    dungeon_map_canvas.pack(pady=6)
    inv_btn.pack(pady=4)
    save_btn.pack(pady=2)
    quit_btn.pack(pady=2)
    refresh_inventory_button()
    refresh_hero_display()
    refresh_skill_buttons()
    refresh_dungeon_map()

    log_feed.config(text=f"📂 Partie chargée (emplacement {slot}) ! Bon retour, {hero['nom']} (Salle {current_room}/{ROOMS_BEFORE_BOSS}).", fg="lightgreen")
    generate_path_choices()


def open_load_dialog():
    # Fenêtre de choix de l'emplacement à charger
    win = tk.Toplevel(window)
    win.title("📂 Charger une partie")
    win.configure(bg="#2d1b0f")
    win.geometry("440x260")
    try:
        win.transient(window)
    except tk.TclError:
        pass

    tk.Label(win, text="📂 CHOISIR UNE SAUVEGARDE", font=("Arial", 13, "bold"), bg="#2d1b0f", fg="gold").pack(pady=8)

    for slot in range(1, SAVE_SLOTS + 1):
        summary = read_save_summary(slot)
        row = tk.Frame(win, bg="#3e2a17")
        row.pack(fill="x", padx=10, pady=4)
        tk.Label(
            row, text=f"Emplacement {slot} : {summary or '-- vide --'}", bg="#3e2a17", fg="white",
            anchor="w", wraplength=280, justify="left"
        ).pack(side="left", padx=6, fill="x", expand=True)
        btn = tk.Button(
            row, text="Charger", bg="#4682b4", fg="white",
            command=lambda s=slot: (win.destroy(), load_game_from_slot(s))
        )
        if summary is None:
            btn.config(state="disabled", bg="grey")
        btn.pack(side="left", padx=4)

    tk.Button(win, text="Annuler", bg="#666666", fg="white", command=win.destroy).pack(pady=10)


def confirm_return_to_menu():
    # Demande confirmation avant d'abandonner la partie en cours (évite les clics accidentels)
    if hero is None:
        return_to_menu()
        return

    confirm_win = tk.Toplevel(window)
    confirm_win.title("Abandonner la partie ?")
    confirm_win.configure(bg="#2d1b0f")
    confirm_win.geometry("380x150")
    confirm_win.resizable(False, False)
    try:
        confirm_win.transient(window)
        confirm_win.grab_set()
    except tk.TclError:
        pass

    tk.Label(
        confirm_win,
        text="⚠️ Retourner au menu abandonnera\nta progression actuelle (si non sauvegardée).",
        bg="#2d1b0f", fg="white", font=("Arial", 10, "bold"), justify="center"
    ).pack(pady=18)

    btn_row = tk.Frame(confirm_win, bg="#2d1b0f")
    btn_row.pack(pady=5)

    def do_confirm():
        try:
            confirm_win.grab_release()
        except tk.TclError:
            pass
        confirm_win.destroy()
        return_to_menu()

    def do_cancel():
        try:
            confirm_win.grab_release()
        except tk.TclError:
            pass
        confirm_win.destroy()

    tk.Button(btn_row, text="Abandonner", bg="#8b0000", fg="white", command=do_confirm).pack(side="left", padx=8)
    tk.Button(btn_row, text="Annuler", bg="#666666", fg="white", command=do_cancel).pack(side="left", padx=8)


def return_to_menu():
    # Réinitialise totalement la partie
    global hero, current_monster, current_room, image_display_label

    hero = None
    current_monster = None
    current_room = 0

    monster_bar_canvas.pack_forget()
    combat_frame.pack_forget()
    loot_frame.pack_forget()
    frame_chemins.pack_forget()
    frame_taverne.pack_forget()
    frame_evenement.pack_forget()
    frame_marchand.pack_forget()
    reset_btn.pack_forget()
    status_label.pack_forget()
    hero_display_frame.pack_forget()
    dungeon_map_canvas.pack_forget()
    inv_btn.pack_forget()
    save_btn.pack_forget()
    quit_btn.pack_forget()
    play_ambient_music()

    if image_display_label is not None:
        image_display_label.destroy()
        image_display_label = None

    entree_nom.delete(0, tk.END)
    log_feed.config(text="Bienvenue dans le Donjon de Naheulbeuk. Crée ton aventurier.", fg="white")
    frame_menu_creation.pack(pady=10)
    refresh_load_button_state()
    refresh_race_thumbnails()


# --- FENÊTRE PRINCIPALE ---
window = tk.Tk()
window.title("Le Donjon de Naheulbeuk")
window.geometry("1100x960")
window.configure(bg="#2d1b0f")

# Chargement des images après création de la fenêtre Tk
# C'est plus fiable pour ImageTk.PhotoImage
victory_image_ref = load_game_image("victoire.png")
gameover_image_ref = load_game_image("gameover.png")

init_audio()

top_bar = tk.Frame(window, bg="#2d1b0f")
top_bar.pack(fill="x", pady=10, padx=10)

title_label = tk.Label(
    top_bar,
    text="🏰 LE DONJON DE NAHEULBEUK 🏰",
    font=("Arial", 20, "bold"),
    bg="#2d1b0f",
    fg="gold"
)
title_label.pack(side="left", expand=True)

mute_btn = tk.Button(
    top_bar,
    text="🔊",
    font=("Arial", 10, "bold"),
    bg="#4b0082",
    fg="white",
    command=toggle_music_mute
)
mute_btn.pack(side="right")

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

hero_display_frame = tk.Frame(window, bg="#2d1b0f")

portrait_canvas = tk.Canvas(hero_display_frame, width=90, height=92, bg="#1a1a1a", highlightthickness=0)
portrait_canvas.pack(side="left", padx=(0, 10))

hero_right_column = tk.Frame(hero_display_frame, bg="#2d1b0f")
hero_right_column.pack(side="left")

hero_bars_canvas = tk.Canvas(hero_right_column, width=860, height=92, bg="#1a1a1a", highlightthickness=0)
hero_bars_canvas.pack()

equipment_icons_canvas = tk.Canvas(hero_right_column, width=860, height=54, bg="#1a1a1a", highlightthickness=0)
equipment_icons_canvas.pack(pady=(4, 0))

dungeon_map_canvas = tk.Canvas(window, width=960, height=150, bg="#1a1a1a", highlightthickness=0)

inv_btn = tk.Button(
    window,
    text="🎒 Inventaire (0)",
    font=("Arial", 10, "bold"),
    bg="#4b0082",
    fg="white",
    command=open_inventory
)

save_btn = tk.Button(
    window,
    text="💾 Sauvegarder",
    font=("Arial", 10, "bold"),
    bg="#2e8b57",
    fg="white",
    command=open_save_dialog
)

quit_btn = tk.Button(
    window,
    text="🔄 Retour au Menu",
    font=("Arial", 10, "bold"),
    bg="#8b0000",
    fg="white",
    command=confirm_return_to_menu
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

load_btn = tk.Button(
    frame_input,
    text="📂 Charger",
    font=("Arial", 11, "bold"),
    command=open_load_dialog,
    bg="#4682b4",
    fg="white"
)
load_btn.pack(side="left", padx=5)

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
    r_btn = tk.Button(frame_race, text=r_node, compound="top", bg="#f0f0f0", fg="black")
    r_btn.config(command=lambda r=r_node, b=r_btn: choose_race(r, b))
    r_btn.pack(side="left", padx=2)
    race_buttons[r_node] = r_btn

rand_r_btn = tk.Button(frame_race, text="🎲 Aléatoire", bg="#32cd32", fg="white", command=lambda: choose_race("Aléatoire", rand_r_btn))
rand_r_btn.pack(side="left", padx=2)

refresh_race_thumbnails()

frame_classe = tk.Frame(frame_menu_creation, bg="#2d1b0f")
frame_classe.pack(pady=2)

for c_node in classes:
    c_btn = tk.Button(frame_classe, text=c_node)
    c_btn.config(command=lambda c=c_node, b=c_btn: choose_class(c, b))
    c_btn.pack(side="left", padx=2)

rand_c_btn = tk.Button(frame_classe, text="🎲 Aléatoire", bg="#32cd32", fg="white", command=lambda: choose_class("Aléatoire", rand_c_btn))
rand_c_btn.pack(side="left", padx=2)

frame_difficulte = tk.Frame(frame_menu_creation, bg="#2d1b0f")
frame_difficulte.pack(pady=2)

tk.Label(frame_difficulte, text="Difficulté :", font=("Arial", 10, "bold"), bg="#2d1b0f", fg="white").pack(side="left", padx=5)

diff_facile_btn = tk.Button(frame_difficulte, text="😌 Facile", command=lambda: choose_difficulty("Facile", diff_facile_btn))
diff_facile_btn.pack(side="left", padx=2)

diff_normal_btn = tk.Button(frame_difficulte, text="⚔️ Normal", bg="#ff8c00", fg="white", command=lambda: choose_difficulty("Normal", diff_normal_btn))
diff_normal_btn.pack(side="left", padx=2)

diff_difficile_btn = tk.Button(frame_difficulte, text="💀 Difficile", command=lambda: choose_difficulty("Difficile", diff_difficile_btn))
diff_difficile_btn.pack(side="left", padx=2)

# --- CHOIX DES CHEMINS ---
frame_chemins = tk.Frame(window, bg="#2d1b0f")

path_left_btn = tk.Button(frame_chemins, text="", font=("Arial", 11), width=24, bg="#5c4033", fg="white", command=lambda: choose_path("left"))
path_left_btn.pack(side="left", padx=5)

path_mid_btn = tk.Button(frame_chemins, text="", font=("Arial", 11), width=24, bg="#5c4033", fg="white", command=lambda: choose_path("middle"))
path_mid_btn.pack(side="left", padx=5)

path_right_btn = tk.Button(frame_chemins, text="", font=("Arial", 11), width=24, bg="#5c4033", fg="white", command=lambda: choose_path("right"))
path_right_btn.pack(side="left", padx=5)

# --- COMBAT ---
monster_bar_canvas = tk.Canvas(window, width=960, height=36, bg="#1a1a1a", highlightthickness=0)

combat_frame = tk.Frame(window, bg="#2d1b0f")

attack_btn = tk.Button(combat_frame, text="⚔️ ATTAQUER", font=("Arial", 11, "bold"), bg="#8b0000", fg="white", width=12, command=execute_melee_attack)
attack_btn.pack(side="left", padx=4)

skill1_btn = tk.Button(combat_frame, text="", font=("Arial", 11, "bold"), bg="#4b0082", fg="white", width=22, command=lambda: cast_skill(1))
skill1_btn.pack(side="left", padx=4)

skill2_btn = tk.Button(combat_frame, text="", font=("Arial", 11, "bold"), bg="grey", fg="white", width=22, command=lambda: cast_skill(2))
skill2_btn.pack(side="left", padx=4)

flee_btn = tk.Button(combat_frame, text="🏃 FUIR", font=("Arial", 11, "bold"), bg="orange", fg="black", width=10, command=execute_flee_action)
flee_btn.pack(side="left", padx=4)

potion_btn = tk.Button(combat_frame, text="🧪 Potion", font=("Arial", 11, "bold"), bg="#2e8b57", fg="white", width=10, command=use_potion)
potion_btn.pack(side="left", padx=4)

mana_potion_btn = tk.Button(combat_frame, text="🔮 Mana", font=("Arial", 11, "bold"), bg="#2e8b57", fg="white", width=10, command=use_mana_potion)
mana_potion_btn.pack(side="left", padx=4)

# --- LOOT ---
loot_frame = tk.Frame(window, bg="#2d1b0f")

equip_btn = tk.Button(loot_frame, text="🎒 ÉQUIPER", font=("Arial", 12, "bold"), bg="#4a7c59", fg="white", width=12, command=accept_loot_item)
equip_btn.pack(side="left", padx=5)

store_btn = tk.Button(loot_frame, text="🧳 RANGER", font=("Arial", 12, "bold"), bg="#4682b4", fg="white", width=12, command=store_loot_item)
store_btn.pack(side="left", padx=5)

discard_btn = tk.Button(loot_frame, text="🗑️ JETER", font=("Arial", 12, "bold"), bg="#8b0000", fg="white", width=12, command=discard_loot_item)
discard_btn.pack(side="left", padx=5)

# --- TAVERNE ---
frame_taverne = tk.Frame(window, bg="#2d1b0f")

btn_dormir = tk.Button(frame_taverne, text="🛌 Dormir (15 Or)", font=("Arial", 11, "bold"), bg="#4a7c59", fg="white", command=lambda: taverne_action("dormir"))
btn_dormir.pack(side="left", padx=5)

btn_biere = tk.Button(frame_taverne, text="🍺 Bière (10 Or)", font=("Arial", 11, "bold"), bg="#1e90ff", fg="white", command=lambda: taverne_action("biere"))
btn_biere.pack(side="left", padx=5)

btn_rien_taverne = tk.Button(frame_taverne, text="🚶 Ne rien faire", font=("Arial", 11, "bold"), bg="#666666", fg="white", command=lambda: taverne_action("rien"))
btn_rien_taverne.pack(side="left", padx=5)

# --- ÉVÉNEMENT PATROUILLE ---
frame_evenement = tk.Frame(window, bg="#2d1b0f")

btn_discret = tk.Button(frame_evenement, text="🕵️ Option A (Discrétion)", font=("Arial", 11, "bold"), bg="#4b0082", fg="white", command=lambda: evenement_choix("discret"))
btn_discret.pack(side="left", padx=5)

btn_baston = tk.Button(frame_evenement, text="🪓 Option B (Froncer)", font=("Arial", 11, "bold"), bg="#8b0000", fg="white", command=lambda: evenement_choix("baston"))
btn_baston.pack(side="left", padx=5)

# --- MARCHAND ---
frame_marchand = tk.Frame(window, bg="#2d1b0f")

frame_marchand_achat = tk.Frame(frame_marchand, bg="#2d1b0f")
frame_marchand_achat.pack(pady=2)

buy_potion_btn = tk.Button(frame_marchand_achat, text="🧪 Potion de Soin (15 or)", font=("Arial", 10, "bold"), bg="#4a7c59", fg="white", command=buy_potion_from_merchant)
buy_potion_btn.pack(side="left", padx=3)

buy_food_btn = tk.Button(frame_marchand_achat, text="🍖 Ration de Voyage (8 or)", font=("Arial", 10, "bold"), bg="#4a7c59", fg="white", command=buy_food_from_merchant)
buy_food_btn.pack(side="left", padx=3)

buy_mana_btn = tk.Button(frame_marchand_achat, text="🔮 Fiole de Mana (12 or)", font=("Arial", 10, "bold"), bg="#4a7c59", fg="white", command=buy_mana_from_merchant)
buy_mana_btn.pack(side="left", padx=3)

buy_armure_btn = tk.Button(frame_marchand_achat, text="🥋 Armure", font=("Arial", 10, "bold"), bg="#8b4513", fg="white", command=lambda: buy_equipment_from_merchant("armure"))
buy_armure_btn.pack(side="left", padx=3)

buy_casque_btn = tk.Button(frame_marchand_achat, text="⛑️ Casque", font=("Arial", 10, "bold"), bg="#8b4513", fg="white", command=lambda: buy_equipment_from_merchant("casque"))
buy_casque_btn.pack(side="left", padx=3)

buy_bottes_btn = tk.Button(frame_marchand_achat, text="🥾 Bottes", font=("Arial", 10, "bold"), bg="#8b4513", fg="white", command=lambda: buy_equipment_from_merchant("bottes"))
buy_bottes_btn.pack(side="left", padx=3)

frame_marchand_bas = tk.Frame(frame_marchand, bg="#2d1b0f")
frame_marchand_bas.pack(pady=2)

sell_btn_marchand = tk.Button(frame_marchand_bas, text="🪙 Vendre des objets", font=("Arial", 10, "bold"), bg="#daa520", fg="black", command=open_merchant_sell_window)
sell_btn_marchand.pack(side="left", padx=5)

leave_merchant_btn = tk.Button(frame_marchand_bas, text="🚪 Partir", font=("Arial", 10, "bold"), bg="#666666", fg="white", command=leave_merchant)
leave_merchant_btn.pack(side="left", padx=5)

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
refresh_load_button_state()
play_ambient_music()
window.mainloop()ICATION ---
window.mainloop()
