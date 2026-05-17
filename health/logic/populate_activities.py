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
        },
        {
            'title': 'The Monkey and the Crocodile',
            'template_text': 'A clever monkey lived on a beautiful rose-apple tree by the bank of a river. He became friends with a crocodile named Karalavaktra. They spent hours talking and sharing delicious rose-apples. One day, the crocodile took some apples home for his wife. His wife, intrigued by the sweetness of the fruit, demanded to eat the monkey\'s heart, arguing that it must be incredibly sweet. The crocodile reluctantly agreed and invited the monkey to his home for dinner, carrying him on his back. Halfway across the deep river, the crocodile confessed the truth. Thinking quickly, the monkey said, "Oh dear friend, why didn\'t you tell me sooner? I leave my heart safely stored in the hollow of my rose-apple tree! We must return to fetch it." The crocodile believed him and turned back. As soon as they reached the shore, the monkey climbed up to safety and told the foolish crocodile that one\'s heart is never kept outside. The monkey\'s quick wit had saved his life.',
            'region_tag': 'SOUTH_INDIA',
            'moral_lesson': 'Presence of mind and quick thinking can overcome even the deadliest trap.'
        },
        {
            'title': 'The Crane and the Crab',
            'template_text': 'An old crane lived by a large lake but was too weak to catch fish. To survive, he devised a plan. He stood by the water\'s edge looking extremely sad. When the fish and a friendly crab asked him what was wrong, he replied, "I have heard that astrologers predict a twelve-year drought, and this beautiful lake will dry up completely. I feel terrible for all of you." Terrified, the water creatures begged the crane for help. He offered to carry them one by one to a larger, perennial lake nearby. The fish gladly agreed. Everyday, the crane carried a few fish, but instead of taking them to a lake, he flew to a flat rock and ate them. One day, the crab asked to be relocated. As they flew, the crab looked down and saw no lake, only a rock covered in fish bones. Realizing the crane\'s treachery, the crab used his sharp claws to pinch the crane\'s neck tightly, killing the deceitful bird. The crab walked back to the old lake and saved his fellow friends.',
            'region_tag': 'COASTAL',
            'moral_lesson': 'Deceit never pays in the end; a wicked plan backfires on the plotter.'
        },
        {
            'title': 'The Blue Jackal',
            'template_text': 'Chandrava was a hungry jackal wandering in search of food near a village when he was chased by a pack of fierce stray dogs. Running for his life, he scrambled into the house of a local washerman and fell into a large vat full of deep blue dye. When he climbed out, he was completely blue from nose to tail. In the forest, all the other animals were terrified of this strange, celestial creature. Seeing their fear, the jackal declared himself the king appointed by the heavens. He enjoyed the power, receiving food and praise from lions, tigers, and elephants alike. One evening, a pack of jackals began to howl in the distance. Overjoyed, the blue jackal forgot his disguise and began to howl along with them. Hearing his true voice, the other forest animals realized he was just an ordinary jackal and chased him out of the jungle.',
            'region_tag': 'WEST_INDIA',
            'moral_lesson': 'True identity cannot be hidden behind artificial disguises forever.'
        },
        {
            'title': 'The Four Friends and the Hunter',
            'template_text': 'Once in a peaceful forest, a deer, a crow, a turtle, and a mouse were the best of friends. They met everyday to talk and share food. One day, the deer got trapped in a hunter\'s strong net. The crow spotted him and flew back to tell the others. Quickly, the crow carried the mouse on his back to the trap, and the mouse began to gnaw through the thick ropes with his sharp teeth. Just as the deer was freed, the slow-moving turtle arrived. The hunter returned and, seeing the deer gone, captured the slow turtle instead. To save the turtle, the deer lay down near the path, pretending to be dead, while the crow pretended to peck at his eyes. The hunter greedily ran towards the deer, leaving his bag containing the turtle behind. The mouse quickly gnawed the bag open and freed the turtle. When the hunter got close, the deer sprang up and ran away, leaving the hunter empty-handed and amazed by the power of true friendship.',
            'region_tag': 'NORTH_INDIA',
            'moral_lesson': 'Unity and collective effort can defeat the greatest challenges.'
        }
    ]

    for story_data in stories:
        BedtimeStory.objects.get_or_create(title=story_data['title'], defaults=story_data)

    print("Successfully seeded Brain Development data!")

if __name__ == "__main__":
    seed_brain_data()
