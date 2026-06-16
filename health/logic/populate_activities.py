import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'childcare_project.settings')
django.setup()

from health.models import OfflineActivity, BedtimeStory

def seed_brain_data():
    # 1. Seed Offline Activities for both old and new explicit age brackets
    activities = [
        # Sensory/Tracking (<6 Months) - NEW
        {
            'title': 'High-Contrast Card Tracking',
            'description': 'Show the baby high-contrast black and white drawings (like a simple circle or smiley face) printed or drawn on a sheet of paper. Hold it 8-12 inches from their face and slowly move it from left to right to watch them track it.',
            'age_tier': 'sensory',
            'materials_needed': 'White paper, black charcoal or sketch pen',
            'developmental_benefit': 'Promotes early visual pathway development and ocular muscle coordination.',
            'risk_if_missed': 'Slower focus adjustments and eye muscle control if visual stimulation is limited.'
        },
        {
            'title': 'Sound Location Exploration',
            'description': 'Shake a simple homemade rattle (a plastic bottle filled with mustard seeds or pebbles) gently on the left side of the baby\'s head out of their direct line of sight. Wait for them to turn their head, then repeat on the right side.',
            'age_tier': 'sensory',
            'materials_needed': 'Plastic bottle, small stones or dried beans',
            'developmental_benefit': 'Develops sound localization, auditory processing, and cognitive curiosity.',
            'risk_if_missed': 'Delayed auditory-spatial orientation and responsiveness to human voice cues.'
        },
        # Object permanence/grasping (6-12 Months) - NEW
        {
            'title': 'Hide & Seek Toy Quest',
            'description': 'Show the baby a bright colored toy, then cover it with a small clean towel or cup while they are watching. Ask "Where did it go?" and encourage them to pull the cloth off to find the hidden treasure.',
            'age_tier': 'grasping',
            'materials_needed': 'A favorite toy, a small light towel or soft cloth',
            'developmental_benefit': 'Teaches object permanence (concept that objects continue to exist even when unseen).',
            'risk_if_missed': 'Delays in problem-solving reasoning and basic spatial object concepts.'
        },
        {
            'title': 'The Crinkle Paper Squeeze',
            'description': 'Provide the baby with clean, noisy wrapping paper or brown grocery bags. Let them squeeze, crunch, and release it with their fingers to hear the crackling sound and feel the changing shape.',
            'age_tier': 'grasping',
            'materials_needed': 'Clean dry paper sheets',
            'developmental_benefit': 'Builds fine motor strength, hand grip, and cause-and-effect reasoning.',
            'risk_if_missed': 'Underdeveloped finger muscles and weaker hand grip during the early grasp transition phase.'
        },
        # Toddler/sorting (1-3 Years) - NEW
        {
            'title': 'Nature Sort: Stones and Leaves',
            'description': 'Collect a handful of dry leaves and small smooth stones from the garden. Help the child sort them into two separate baskets—one for the flat green leaves and another for the heavy round stones.',
            'age_tier': 'toddler',
            'materials_needed': 'Stones, dry leaves, two small containers',
            'developmental_benefit': 'Fosters categorization logic, comparison skills, and physical tactile discrimination.',
            'risk_if_missed': 'Slower development of mathematical categorization and logical sorting frameworks.'
        },
        {
            'title': 'Spoon Size Matching Game',
            'description': 'Gather a mix of small tea spoons and larger serving spoons from the kitchen. Show the toddler how to place the small spoons in one cup and the large spoons in another.',
            'age_tier': 'toddler',
            'materials_needed': 'Diverse sizes of kitchen spoons, two plastic mugs',
            'developmental_benefit': 'Develops spatial comparison, size discrimination, and cognitive classification.',
            'risk_if_missed': 'Slower recognition of geometric differences and dimensional sorting logic.'
        },
        # Pre-schooler/modeling (3-6 Years) - NEW
        {
            'title': 'Wheat Dough Atta Modeling',
            'description': 'Give your child a small ball of clean wheat dough (atta) from the kitchen. Show them how to roll it into long ropes, round balls, and simple shapes like a snake, a star, or a bird.',
            'age_tier': 'preschool',
            'materials_needed': 'Wheat flour dough (atta), rolling pin or wooden board',
            'developmental_benefit': 'Strengthens intrinsic hand muscles, visual-spatial layout skills, and creative modeling.',
            'risk_if_missed': 'Fine motor and hand-eye coordination delays that can affect pencil grip and writing neatness.'
        },
        {
            'title': 'Twig House Engineering',
            'description': 'Use fallen twigs and dry leaves to construct a tiny structure on the flat ground. Encourage the child to build the side walls and lay down the leaf roof to shield a toy figure.',
            'age_tier': 'preschool',
            'materials_needed': 'Dry twigs, leaves, grass, a toy figure',
            'developmental_benefit': 'Encourages spatial engineering thoughts, stability awareness, and concentration.',
            'risk_if_missed': 'Reduced creative spatial problem-solving skills and hand dexterity.'
        },
        # School support/logic (6-11 Years) - NEW
        {
            'title': 'Stick Shadow Sundial',
            'description': 'Plant a straight stick in the dirt in a sunny spot. Every hour, place a stone at the tip of the stick\'s shadow and write down the hour on the ground. Discuss how the shadow moves as the earth rotates.',
            'age_tier': 'school',
            'materials_needed': 'A straight stick, small flat stones, sunny open patch',
            'developmental_benefit': 'Applies active scientific reasoning, environmental cycles, and spatial understanding of time.',
            'risk_if_missed': 'Poorer understanding of natural sciences, astronomy, and solar relationships.'
        },
        {
            'title': 'Family Story Tree Mapping',
            'description': 'Help your child interview their grandparents or parents about older ancestors. Together, draw a branching family tree map using handprints, color codes, and names, and let them trace the family lineage.',
            'age_tier': 'school',
            'materials_needed': 'Paper, pencil, colorful sketches or leaf stamps',
            'developmental_benefit': 'Fosters historical sequencing, chronological logic, social bonds, and verbal mapping.',
            'risk_if_missed': 'Weaker logical mapping, ordering capabilities, and community identity concepts.'
        },
        # Old tiers for backward compatibility
        {
            'title': 'Texture Touch Discovery',
            'description': 'Gather different local fabrics like a cotton dhoti, a jute sack, and a silk scarf. Let the baby touch each one while you describe the feeling (rough, soft, smooth).',
            'age_tier': 'infant',
            'materials_needed': 'Jute sack, Cotton cloth, Silk or smooth fabric',
            'developmental_benefit': 'Develops tactile sensory processing and early vocabulary.',
            'risk_if_missed': 'Delayed sensory integration can lead to sensitivity to different textures later.'
        },
        {
            'title': 'The Great Grain Sort',
            'description': 'Mix a small amount of three different local grains (like Ragi, Rice, and Dal) in a bowl. Ask your child to sort them into three separate smaller bowls.',
            'age_tier': 'early',
            'materials_needed': 'Uncooked grains (Rice, Dal, Ragi), Small bowls',
            'developmental_benefit': 'Enhances fine motor skills and basic categorization logic.',
            'risk_if_missed': 'Fine motor delays can impact writing skills in early schooling.'
        },
        {
            'title': 'Map of the Village Market',
            'description': 'Take your child to the local market. Ask them to draw a rough "Hero Map" showing where the grains, vegetables, and tools are sold.',
            'age_tier': 'preteen',
            'materials_needed': 'Paper, Charcoal or Pencil',
            'developmental_benefit': 'Builds spatial awareness and community navigation skills.',
            'risk_if_missed': 'Lack of spatial reasoning can hinder mathematical and geographic learning.'
        }
    ]

    for act_data in activities:
        OfflineActivity.objects.get_or_create(title=act_data['title'], defaults=act_data)

    # 2. Seed Bedtime Stories (Expanding with [Name] and [Locality] and distinct UI themes)
    stories = [
        # North India
        {
            'title': 'The Clever Rabbit and the Jungle Well',
            'template_text': 'Deep in the jungles near [Locality], there lived a proud lion Bhasuraka who hunted all the animals. One day, a clever child named [Name] advised the animals to use their intelligence. When it was the small rabbit\'s turn to visit the lion, the rabbit arrived very late. "Another lion has challenged you," the rabbit told the angry Bhasuraka. The rabbit led Bhasuraka to a deep well. Hearing his own echo and seeing his own reflection inside, the lion jumped in! Thanks to [Name]\'s wise advice and the rabbit\'s wit, the jungle of [Locality] was peaceful forever.',
            'region_tag': 'NORTH_INDIA',
            'moral_lesson': 'Intelligence is more powerful than brute strength.'
        },
        {
            'title': 'The Gold-Giving Sparrow of [Locality]',
            'template_text': 'In the beautiful hills of [Locality], a little bird built her nest in the window of a kind child named [Name]. Every morning, [Name] shared a handful of ragi and wheat grains with the sparrow. In return, the magical sparrow dropped a single golden grain into the courtyard each evening. One day, a greedy merchant tried to capture the sparrow, but [Name] released it back to the blue forest. The sparrow flew high and sang a song, teaching that pure love and generosity are the greatest wealth in [Locality].',
            'region_tag': 'NORTH_INDIA',
            'moral_lesson': 'True kindness is selfless, and greed destroys true beauty.'
        },
        # South India
        {
            'title': 'The Magic Drum under the Banyan Tree',
            'template_text': 'In a green, fertile village of [Locality], a child named [Name] found an ancient wooden drum hidden in the roots of a giant banyan tree. When [Name] tapped the drum with rhythm, the music was so sweet that rain clouds formed and watered the dry paddy fields. The happy farmers rejoiced and thanked [Name], who promised to play the drum whenever [Locality] needed life and green crops. The banyan forest echoed with sweet songs.',
            'region_tag': 'SOUTH_INDIA',
            'moral_lesson': 'Music and harmony with nature can bring healing to the earth.'
        },
        {
            'title': 'The Wise Elephant and the Hidden River',
            'template_text': 'During a very dry summer in the village of [Locality], the water streams had all dried up. A young child named [Name] walked into the forest and met Gajendra, a wise old elephant. [Name] gently offered the last bit of jaggery to Gajendra. Touched by the kid\'s kindness, Gajendra used his large ears to listen deep into the forest floor. He marched to a spot, dug with his tusks, and uncovered a sparkling, clear underground river! [Name] ran back to lead all the villagers of [Locality] to this fresh water, and they lived in deep friendship with the forest giants.',
            'region_tag': 'SOUTH_INDIA',
            'moral_lesson': 'Patience, respect, and kindness toward animals unlock hidden gifts.'
        },
        # Coastal Belt
        {
            'title': 'The Thirsty Crow and the Magic Water',
            'template_text': 'Under the warm sun of the coastal shore in [Locality], a thirsty crow searched for water. He found a pitcher behind the house of [Name], but the water level was too low. Instead of giving up, the crow asked [Name] for help. [Name] showed him smooth black pebbles lying by the sea. One by one, the crow dropped the pebbles into the pitcher. The water rose to the brim! The crow drank his fill and cawed happily, teaching the children of [Locality] that where there is a will, there is always a way.',
            'region_tag': 'COASTAL',
            'moral_lesson': 'Necessity and creative effort are the keys to overcoming obstacles.'
        },
        {
            'title': 'The Ocean Queen and the Pearl Oyster',
            'template_text': 'A brave young kid named [Name] walked along the sandy beaches of [Locality] picking up plastic trash. Suddenly, a giant oyster washed up, containing a glittering pearl. "This is the Ocean Queen\'s gift," a sea dolphin whispered to [Name]. The Ocean Queen appeared and said, "Because you keep our shores of [Locality] clean, I grant you this magic shell. It will always warn you when the high tide is coming." [Name] became the hero protector of the shores.',
            'region_tag': 'COASTAL',
            'moral_lesson': 'Protecting our marine environment brings safety and hidden treasures.'
        },
        # West India
        {
            'title': 'The Golden Sand Camel of [Locality]',
            'template_text': 'In the golden, sandy desert surrounding [Locality], a beautiful camel named Maru carried precious bags of salt. A kind child named [Name] always kept a bowl of cool water and fresh bajra stalks ready for Maru. One night, a fierce sandstorm swept through the region, hiding the oasis path. Using his excellent memory, Maru guided [Name] safely through the shifting dunes of [Locality] back to the warmth of home. They celebrated their escape with sweet jaggery.',
            'region_tag': 'WEST_INDIA',
            'moral_lesson': 'Loyalty and endurance can steer us safely through the fiercest storms.'
        },
        {
            'title': 'The Peacock\'s Rain Dance',
            'template_text': 'In the arid dry fields of [Locality], crops were dying and everyone prayed for rain. A young child named [Name] gathered the children to sing traditional songs. Hearing their sweet voices, Mayura, a majestic blue peacock, spread his feathers and began a beautiful rain dance. As Mayura spun, lightning flashed, and sweet cooling rain began to fall over the parched lands of [Locality]. [Name] and the peacock danced together in the muddy puddles, celebrating the return of green life.',
            'region_tag': 'WEST_INDIA',
            'moral_lesson': 'Community unity and joy can summon the positive forces of nature.'
        },
        # East India
        {
            'title': 'The Bamboo Flute of [Locality]',
            'template_text': 'In a quiet village surrounded by green tea gardens in [Locality], a child named [Name] loved to play a small bamboo flute. One afternoon, a stray tiger walked out of the hills. Instead of running, [Name] calmly sat down and played a soft, soothing melody. The tiger sat down, closed its eyes, and listened peacefully before returning back to the mountains. The village elders of [Locality] praised the child, realizing that gentle harmony wins over wild fear.',
            'region_tag': 'EAST_INDIA',
            'moral_lesson': 'Gentleness and calm resolve can pacify even the fiercest anger.'
        },
        {
            'title': 'The River Dolphin\'s Magic Quest',
            'template_text': 'While playing near the large river flowing through [Locality], a child named [Name] accidentally dropped a silver family ring into the deep waters. Seeing [Name]\'s tears, a playful Ganges river dolphin swam up. The dolphin swam deep into the riverbed, retrieved the sparkling ring, and placed it gently in [Name]\'s hand. In return, [Name] promised to keep the river clean from plastics, ensuring a safe home for the dolphins of [Locality].',
            'region_tag': 'EAST_INDIA',
            'moral_lesson': 'A helpful hand returned to nature builds a bridge of lifetime protection.'
        },
        # Central India
        {
            'title': 'The Glowing Firefly of the Plateau',
            'template_text': 'One dark night, a child named [Name] got lost in the dense sal forests of [Locality]. Just as [Name] began to worry, a tiny firefly named Jugnu appeared, glowing with a soft amber light. Jugnu called hundreds of other fireflies, creating a glowing path that lit up the entire forest floor of [Locality]. [Name] followed this magical light safely back to their parents. They realized that no matter how small you are, you can light up someone\'s dark path.',
            'region_tag': 'CENTRAL_INDIA',
            'moral_lesson': 'No act of help is too small to make a vital difference in the dark.'
        },
        {
            'title': 'The Banyan Tree\'s Ancient Whispers',
            'template_text': 'On a rocky plateau in [Locality], stands a giant banyan tree that is five hundred years old. A child named [Name] loved to sit in its cool shade. The tree would whisper old fables of ancient kings who built great stone forts. [Name] learned about history, agriculture, and wisdom from these whispers. [Name] shared these stories with the school friends of [Locality], ensuring the ancient wisdom of the plateau would never be forgotten.',
            'region_tag': 'CENTRAL_INDIA',
            'moral_lesson': 'Respecting our natural heritage and listing to elder wisdom builds a strong foundation.'
        }
    ]

    for story_data in stories:
        BedtimeStory.objects.update_or_create(title=story_data['title'], defaults=story_data)

    print("Successfully seeded dynamic Activities and expanded Fables data!")

if __name__ == "__main__":
    seed_brain_data()
