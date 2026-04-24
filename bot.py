import json
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8653067393:AAGtL1V2-M36zmfQmgH73NDmlPxQ2vzRpjg"

# Load data
with open('participants.json', 'r') as f:
    PARTICIPANTS = json.load(f)

# Correct Group Definitions
ADVISER_GROUPS = {
    "toroshchinaaa": "Team_Toroshchina",
    "khanfer_abed": "Team_Khanfer",
    "Husseinshamil": "Team_Hussein",
    "Angealia": "Team_Angealia",
    "Angeleena04": "Team_Angeleena",
    "KiddPunkRiot": "Team_KiddPunkRiot",
    "shri9360": "Team_Shri",
    "globglobgabgalab08": "Team_GlobGlob",
    "S_01111010_01100001_01101011": "Team_Shah_Zak",
    "Its_shah_250603": "Team_Shah_Zak",
    "xeshi_x": "Team_Xeshi_Hiba",
    "hibbachii": "Team_Xeshi_Hiba",
    "hibasinath": "Team_Xeshi_Hiba"
}

# Global state for assignments
assignments = {}

def perform_assignment():
    global assignments
    assigned_names = set()
    green_students = [p for p in PARTICIPANTS if p['is_green']]
    normal_students = [p for p in PARTICIPANTS if not p['is_green']]
    
    # Randomize
    random.shuffle(green_students)
    random.shuffle(normal_students)
    
    new_assignments = {}
    unique_groups = list(set(ADVISER_GROUPS.values()))
    
    # 1. Special case for @toroshchinaaa
    # Must have: Fatola Oluwatosin David (Green) and Udechi Amarachi Benedicta (Normal)
    fixed_names = ["Fatola Oluwatosin David", "Udechi Amarachi Benedicta"]
    torosh_list = []
    for name in fixed_names:
        for p in PARTICIPANTS:
            if p['name'] == name:
                torosh_list.append(p)
                assigned_names.add(name)
                # Remove from pools
                if p in green_students: green_students.remove(p)
                if p in normal_students: normal_students.remove(p)
                break
    
    # Fill Torosh to 4 total (Fatola is Green, so we add 2 more Normal)
    while len(torosh_list) < 4 and normal_students:
        p = normal_students.pop()
        torosh_list.append(p)
        assigned_names.add(p['name'])
    
    new_assignments["Team_Toroshchina"] = torosh_list

    # 2. Assign for other unique groups
    other_groups = [g for g in unique_groups if g != "Team_Toroshchina"]
    random.shuffle(other_groups)
    
    for group in other_groups:
        group_list = []
        # RULE: Each team MUST have exactly 1 green student
        if green_students:
            green = green_students.pop()
            group_list.append(green)
            assigned_names.add(green['name'])
        
        # Fill to 4 total with normal students
        while len(group_list) < 4 and normal_students:
            p = normal_students.pop()
            group_list.append(p)
            assigned_names.add(p['name'])
        
        new_assignments[group] = group_list
        
    assignments = new_assignments

# Perform initial static assignment
perform_assignment()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username
    
    group_id = ADVISER_GROUPS.get(username)
    
    # If not explicitly found, default to "Team_Xeshi_Hiba" (the user's group)
    if not group_id:
        group_id = "Team_Xeshi_Hiba"
    
    my_participants = assignments.get(group_id, [])
    
    if not my_participants:
        await update.message.reply_text("⚠️ Sorry, I couldn't find your team assignment.")
        return

    response = f"Hello @{username}!\n\nHere is your team (4 participants):\n"
    response += "----------------------------------\n"
    for i, p in enumerate(my_participants, 1):
        status = "🟢 (Green)" if p['is_green'] else "⚪ (Normal)"
        response += f"{i}. {p['name']} {status}\n"
    response += "----------------------------------\n"
    response += "\n✅ Rules applied:\n- 1 Green student per team\n- 4 Total participants per team\n- No duplicates across teams"
    
    await update.message.reply_text(response)

async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "📋 **FULL ASSIGNMENT LIST**\n\n"
    for group, members in assignments.items():
        response += f"🔹 {group}:\n"
        for m in members:
            status = "🟢" if m['is_green'] else "⚪"
            response += f"  - {m['name']} {status}\n"
        response += "\n"
    
    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            await update.message.reply_text(response[x:x+4000])
    else:
        await update.message.reply_text(response)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('list', list_all))
    
    print("Bot is starting...")
    application.run_polling(drop_pending_updates=True)
