import os
import django

# Setup Django environment
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'childcare_project.settings')
django.setup()

from health.models import OfflineActivity, BedtimeStory

def seed_brain_data():
    # 1. Seed Offline Activities
    activities = [
        # Infants (0-2y)
        {
            'title': 'Texture Touch Discovery',
            'description': 'Gather different local fabrics like a cotton dhoti, a jute sack, and a silk scarf. Let the baby touch each one while you describe the feeling (rough, soft, smooth).',
            'age_tier': 'infant',
            'materials_needed': 'Jute sack, Cotton cloth, Silk or smooth fabric',
            'developmental_benefit': 'Develops tactile sensory processing and early vocabulary.',
            'risk_if_missed': 'Delayed sensory integration can lead to sensitivity to different textures later.'
        },
        {
            'title': 'Mirror Mimicry',
            'description': 'Sit with the baby in front of a mirror. Make different faces (happy, sad, surprised) and see if they try to copy you.',
            'age_tier': 'infant',
            'materials_needed': 'A simple household mirror',
            'developmental_benefit': 'Builds self-awareness and social-emotional mimicry skills.',
            'risk_if_missed': 'Mirror play is critical for developing the concept of self and empathy.'
        },
        # Early Childhood (3-6y)
        {
            'title': 'The Great Grain Sort',
            'description': 'Mix a small amount of three different local grains (like Ragi, Rice, and Dal) in a bowl. Ask your child to sort them into three separate smaller bowls.',
            'age_tier': 'early',
            'materials_needed': 'Uncooked grains (Rice, Dal, Ragi), Small bowls',
            'developmental_benefit': 'Enhances fine motor skills and basic categorization logic.',
            'risk_if_missed': 'Fine motor delays can impact writing skills in early schooling.'
        },
        {
            'title': 'Kitchen Shadow Puppets',
            'description': 'In a dim room using a single candle or torch, use kitchen utensils to create shadows on the wall. Ask the child to guess what the "Hero" utensil is doing.',
            'age_tier': 'early',
            'materials_needed': 'Utensils (Ladle, Spoon), Torch or Lamp',
            'developmental_benefit': 'Encourages creative imagination and storytelling structure.',
            'risk_if_missed': 'Imaginative play is essential for complex problem solving later in life.'
        },
        # Pre-Teens (7-11y)
        {
            'title': 'Map of the Village Market',
            'description': 'Take your child to the local market. Ask them to draw a rough "Hero Map" showing where the grains, vegetables, and tools are sold.',
            'age_tier': 'preteen',
            'materials_needed': 'Paper, Charcoal or Pencil',
            'developmental_benefit': 'Builds spatial awareness and community navigation skills.',
            'risk_if_missed': 'Lack of spatial reasoning can hinder mathematical and geographic learning.'
        },
        {
            'title': 'The Solar Sundial',
            'description': 'Place a stick in the ground in an open area. Mark the shadow at 10 AM, 12 PM, and 2 PM using stones. Observe how the shadow "Quest" moves.',
            'age_tier': 'preteen',
            'materials_needed': 'A stick, Small stones, Sunlit area',
            'developmental_benefit': 'Teaches basic astronomy and the concept of time passage.',
            'risk_if_missed': 'Understanding environmental cycles is key to scientific inquiry.'
        }
    ]

    for act_data in activities:
        OfflineActivity.objects.get_or_create(title=act_data['title'], defaults=act_data)

    # 2. Seed Bedtime Stories (Classic Folklore)
    stories = [
        {
            'title': 'The Lion and the Clever Rabbit',
            'template_text': 'Deep in the jungles of India, there lived a fierce lion named Bhasuraka who hunted all the animals. To save themselves, the animals made a pact to send one animal each day. One day, it was a small rabbit\'s turn. The rabbit arrived late and told the lion that another lion had challenged him. Curious and angry, Bhasuraka followed the rabbit to a deep well. "Look inside," the rabbit said. Seeing his own reflection and thinking it was a rival, the lion jumped in and was never seen again. The jungle was finally at peace.',
            'region_tag': 'NORTH_INDIA',
            'moral_lesson': 'Intelligence is more powerful than brute strength.'
        },
        {
            'title': 'The Thirsty Crow and the Magic Pebbles',
            'template_text': 'Under the hot sun of a coastal village, a thirsty crow searched for water. He found a pitcher, but the water level was too low for his beak to reach. Instead of giving up, the crow observed the shore and saw many smooth pebbles. One by one, he picked up the pebbles and dropped them into the pitcher. As the pebbles filled the bottom, the water rose to the top. The crow drank his fill and flew away happily, teaching everyone that where there is a will, there is always a way.',
            'region_tag': 'COASTAL',
            'moral_lesson': 'Necessity is the mother of invention.'
        },
        {
            'title': 'The Loyal Mongoose',
            'template_text': 'In a quiet village surrounded by green fields, a farmer and his wife lived with their baby and a pet mongoose. One day, the wife went to the market, leaving the baby alone with the mongoose. While she was away, a deadly cobra entered the house. The loyal mongoose fought the snake and killed it, saving the baby. When the wife returned and saw blood on the mongoose, she acted in haste. But upon seeing her baby safe and the dead snake nearby, she realized the mongoose had been a true guardian of their home.',
            'region_tag': 'SOUTH_INDIA',
            'moral_lesson': 'Haste makes waste; always verify the truth before acting.'
        }
    ]

    for story_data in stories:
        BedtimeStory.objects.get_or_create(title=story_data['title'], defaults=story_data)

    print("Successfully seeded Brain Development data!")

if __name__ == "__main__":
    seed_brain_data()
