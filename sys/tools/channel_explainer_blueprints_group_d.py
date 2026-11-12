"""Channel Explainer Blueprints for Group D (5 Mindfulness / Parable / Stoic / Empathy Channels).

Provides rich semantic concept mappers and bespoke visual prompt descriptions
for every cue in chanh_niem_ke, loi_sang_soi, minh_triet_song, tam_tinh_dem, and thuong_cho_kheo.
"""

from __future__ import annotations

import re
from typing import Tuple


# ==============================================================================
# 1. CHANH NIEM KE (Mindfulness / Zen Explainer, 260 beats)
# ==============================================================================

def get_explainer_chanh_niem_ke(b_idx: int, text: str, ch_idx: int) -> Tuple[str, str, str]:
    """Return (explainer_type, framing, subject) for chanh_niem_ke."""
    t = text.lower()

    if any(k in t for k in ["thứ nhất", "thứ hai", "thứ ba", "bước một", "bước hai", "bước ba", "ba câu hỏi", "ba bước"]):
        etype = "STEP_ENUMERATION"
        framing = "Three-step sequential enumeration displayed on textured washi paper:"
        if "thứ nhất" in t or "kiểm soát" in t:
            subject = "Question one inscribed with dark sumi ink: Is this circumstance within my direct sphere of control?"
        elif "thứ hai" in t or "năm năm" in t:
            subject = "Question two inscribed with dark sumi ink: Will this event hold any significance in five years?"
        elif "thứ ba" in t or "hành động" in t:
            subject = "Question three inscribed with dark sumi ink: What is the single smallest mindful action I can take right now?"
        else:
            subject = "Three deliberate mindful inquiries systematically filtering out phantom worries from concrete reality"

    elif any(k in t for k in ["thay vì", "trái ngược", "khác biệt", "trong khi", "đối đầu", "so với", "hai nửa", "hai bên", "chứ không"]):
        etype = "SPLIT_COMPARISON"
        framing = "50/50 split-screen comparison:"
        if "cát" in t or "tay" in t or "nắm" in t:
            subject = "on the left, a white-knuckled fist losing fine dry river sand; on the right, an open relaxed palm resting on cedar keeping sand undisturbed"
        elif "giận" in t or "ba giây" in t or "phản ứng" in t:
            subject = "on the left, an impulsive angry retort erupting into sharp crimson sound spikes; on the right, a measured three-second silence in blue ripples"
        elif "bừa bộn" in t or "gọn gàng" in t or "bàn" in t:
            subject = "on the left, a desk cluttered with loose papers and tangled wires; on the right, a clean cedar desk holding one ceramic iris vase"
        elif "tương lai" in t or "quá khứ" in t:
            subject = "on the left, an anxious mind projecting dark shadowy future scenarios; on the right, burned fallen leaves of past regret dissolving into soil"
        elif "trúc" in t or "uốn mình" in t or "gãy" in t:
            subject = "on the left, a rigid dry wooden post snapping under storm wind; on the right, a flexible green bamboo stalk bowing low and springing back unharmed"
        else:
            subject = "on the left, frantic internal resistance struggling against present reality; on the right, calm radical acceptance flowing with circumstance"

    elif any(k in t for k in ["bộ não", "sinh học", "hệ thần kinh", "cơ chế", "khoảng trống", "vòng lặp", "não bộ", "thần kinh", "về mặt sinh học"]):
        etype = "MECHANISM_CUTAWAY"
        framing = "Visual mechanism cutaway diagram illustrating"
        if "thở" in t or "tim" in t or "sinh học" in t:
            subject = "the anatomical vagus nerve pathway: prolonged slow exhalation activating parasympathetic tone and naturally lowering elevated heart rate"
        elif "kích thích" in t or "khoảng trống" in t or "ba giây" in t:
            subject = "the three-second cognitive interval between external stimulus and conscious response, depicted as a glowing golden threshold of choice"
        elif "sinh tồn" in t or "nguy cơ" in t or "báo động" in t:
            subject = "the evolutionary survival alarm: primitive amygdala firing urgent red threat sparks while prefrontal cortex bathes neural circuits in calming gold"
        elif "quá tải" in t or "suy nghĩ" in t:
            subject = "an overloaded cognitive working memory model, comparing limited mental bandwidth to a glass tumbler overflowing with excessive water"
        else:
            subject = "the neurobiological shift from sympathetic fight-or-flight agitation into calm parasympathetic stillness and equilibrium"

    elif any(k in t for k in ["khiến cho", "dẫn đến", "hậu quả", "bắt nguồn", "kết quả", "tạo nên", "biến thành", "tự tiêu biến"]):
        etype = "CAUSE_EFFECT_DIAGRAM"
        framing = "Cause-and-effect flowchart diagram demonstrating"
        if "chấp nhận" in t or "hành động" in t:
            subject = "how radical acceptance of current reality stops the leak of emotional energy, immediately liberating eighty percent of cognitive problem-solving bandwidth"
        elif "nắm chặt" in t or "kiệt sức" in t:
            subject = "how the unconscious psychological urge to micro-manage uncontrollable external variables inevitably produces severe mental exhaustion"
        elif "dọn dẹp" in t or "không gian" in t:
            subject = "how deliberate physical decluttering of one's immediate workspace acts as an immediate catalyst for reducing internal mental static"
        elif "ba giây" in t or "lửa" in t:
            subject = "how pausing for three conscious breaths deprives the spark of anger of reactive fuel, causing the emotional fire to naturally extinguish"
        else:
            subject = "how mindful presence dissolves phantom anxieties while chronic rumination magnifies harmless events into catastrophic crises"

    elif any(k in t for k in ["bạn ngồi", "bước chân", "khép nhẹ", "ngồi lại", "uống một", "dạo bước"]) and b_idx % 5 == 0:
        etype = "SITUATIONAL_ACTION"
        framing = "A mindful practitioner"
        if "bước" in t or "dạo" in t or "chân" in t:
            subject = "walking slowly in traditional wooden sandals along a moss-covered mountain trail, breathing in fresh pine forest air beneath towering cedar trees"
        elif "uống" in t or "nước" in t or "trà" in t:
            subject = "holding a warm rustic ceramic tea cup with both palms, taking a slow deliberate sip while gazing out at gentle afternoon rainfall"
        elif "khép" in t or "mi mắt" in t or "ngồi" in t:
            subject = "resting hands peacefully in dhyana meditation mudra on lap, seated in quiet contemplation on an aged cedar veranda with eyes gently closed"
        else:
            subject = "standing quietly in peaceful posture, watching raindrops create concentric ripples upon a tranquil stone water basin in temple courtyard"

    else:
        etype = "OBJECT_MACRO"
        framing = "Macro close-up shot of"
        if "kính" in t or "mưa" in t or "giọt" in t:
            subject = "crystalline rainwater droplets tracing delicate winding paths down a cold frosted glass windowpane, soft blurred foliage in background"
        elif "ly" in t or "cốc" in t or "nước" in t:
            subject = "a clear crystal water tumbler filled to the convex brim on dark ebony tabletop, liquid dome holding delicately by surface tension"
        elif "đá" in t or "sân chùa" in t or "rêu" in t:
            subject = "ancient moss-covered granite stepping stones in a quiet Buddhist monastery courtyard, wet dark stone reflecting dim evening sky"
        elif "cát" in t or "tay" in t:
            subject = "fine golden river sand slipping smoothly between relaxed fingers resting on a warm polished cedar wood surface"
        elif "trầm" in t or "khói" in t:
            subject = "a slender burning sandalwood incense stick in a celadon ceramic holder, an unmoving vertical ribbon of fragrant smoke rising into still room air"
        elif "trúc" in t or "bão" in t:
            subject = "an emerald green bamboo stalk glistening with rain droplets, bowing gracefully in mountain wind without fracturing"
        elif "bát" in t or "vết nứt" in t or "kintsugi" in t:
            subject = "an antique Japanese ceramic tea bowl mended with shimmering veins of twenty-four karat gold kintsugi lacquer lines"
        elif "điện thoại" in t or "màn hình" in t:
            subject = "a black smartphone resting face-down inside a dark cedar desk drawer, screen completely silent and inactive"
        elif "chuông" in t or "tiếng" in t:
            subject = "a traditional cast-bronze Zen singing bowl with wooden striker resting on an embroidered silk cushion in warm sidelight"
        else:
            subject = "a single fresh camellia blossom floating in a dark earthenware basin of rainwater, perfectly still mirror reflection under soft dawn light"

    return etype, framing, subject


# ==============================================================================
# 2. LOI SANG SOI (Spiritual Parable Explainer, 255 beats)
# ==============================================================================

def get_explainer_loi_sang_soi(b_idx: int, text: str, ch_idx: int) -> Tuple[str, str, str]:
    """Return (explainer_type, framing, subject) for loi_sang_soi."""
    t = text.lower()

    if any(k in t for k in ["ba bài học", "bốn mảnh đất", "thứ nhất", "thứ hai", "thứ ba", "bước"]):
        etype = "STEP_ENUMERATION"
        framing = "Sequential illustrative enumeration detailing"
        if "bốn" in t or "mảnh đất" in t:
            subject = "the four biblical soil conditions: 1. Hardened wayside path, 2. Shallow rocky ledge, 3. Choking thorny thicket, 4. Fertile loamy humus"
        elif "thứ nhất" in t or "gieo" in t:
            subject = "Lesson one: respecting natural gestation time without forcing premature germination before subterranean roots develop"
        elif "thứ hai" in t or "non" in t:
            subject = "Lesson two: protecting fragile early sprouts from scorch and harsh judgment while their stems are tender"
        elif "thứ ba" in t or "chất lượng" in t:
            subject = "Lesson three: continuous patient cultivation of the inner soil quality, allowing the harvest to take care of itself"
        else:
            subject = "three timeless agrarian principles guiding the spiritual growth and fruitful maturity of human character"

    elif any(k in t for k in ["thay vì", "trái ngược", "khác biệt", "trong khi", "đối đầu", "so với", "hai nửa", "hai loại", "không phải"]):
        etype = "SPLIT_COMPARISON"
        framing = "50/50 split-screen comparison:"
        if "vệ đường" in t or "đá" in t or "sỏi" in t:
            subject = "on the left, hard compacted wagon ruts where seeds bounce off dry clay; on the right, soft aerated plowed soil welcoming seed into dark moisture"
        elif "gai" in t or "lúa" in t or "nắng" in t:
            subject = "on the left, wheat stalks suffocating in dense thorny briars; on the right, golden wheat ears flourishing under unobstructed heavenly sunlight"
        elif "nông" in t or "rễ" in t or "cháy" in t:
            subject = "on the left, a shallow root burning against white-hot limestone bedrock; on the right, a deep taproot drinking subterranean aquifer waters"
        elif "hẹp hòi" in t or "rộng lượng" in t:
            subject = "on the left, an anxious hoarder clutching grains in a dark cellar; on the right, a generous sower scattering seed freely across open hills"
        else:
            subject = "on the left, a hardened defensive heart rejecting truth; on the right, a tender receptive spirit bearing thirty, sixty, and hundredfold fruit"

    elif any(k in t for k in ["tầng đất", "cơ chế", "rễ", "ngầm", "giải phẫu", "cấu trúc", "sinh học", "bên trong"]):
        etype = "MECHANISM_CUTAWAY"
        framing = "Agrarian mechanism cutaway diagram illustrating"
        if "rễ" in t or "nước" in t or "hút" in t:
            subject = "the subterranean root architecture: fibrous white root hairs penetrating deep loamy pore spaces to access mineral water reserves"
        elif "đá" in t or "bedrock" in t or "sỏi" in t:
            subject = "a geological cross-section of rocky soil: a two-centimeter dusting of dirt resting over an impenetrable solid limestone ledge"
        elif "gai" in t or "siết" in t:
            subject = "the competitive botanical mechanism of thorny briars: invasive root systems starving wheat of soil nitrogen while prickly canopy blocks light"
        elif "tâm lý" in t or "tầng sâu" in t:
            subject = "a psychological cross-section mapping superficial cynicism, impulsive shallow zeal, and materialistic worry within human consciousness"
        else:
            subject = "the physiological transformation of a dormant dry wheat grain as moisture activates enzymatic growth and embryonic leaf emergence"

    elif any(k in t for k in ["khiến cho", "dẫn đến", "hậu quả", "bắt nguồn", "kết quả", "tạo nên", "bóp nghẹt", "lụi tàn"]):
        etype = "CAUSE_EFFECT_DIAGRAM"
        framing = "Cause-and-effect flowchart diagram demonstrating"
        if "gai" in t or "lo toan" in t or "tiền tài" in t:
            subject = "how unchecked materialistic ambition and everyday anxiety systematically strangle noble aspirations, leaving life spiritually barren"
        elif "nắng" in t or "cạn" in t or "héo" in t:
            subject = "how emotional enthusiasm without deep inner discipline inevitably collapses under the very first heatwave of real-world hardship"
        elif "cày" in t or "mềm" in t or "mùa" in t:
            subject = "how the painful labor of plowing hardened habits and removing hidden stones creates the fertile foundation for an abundant lifelong harvest"
        else:
            subject = "how the condition of the receiving heart directly determines whether truth produces enduring transformation or vanishes without trace"

    elif any(k in t for k in ["người gieo", "bước ra", "bàn tay", "đứng giữa", "quỳ xuống"]) and b_idx % 5 == 0:
        etype = "SITUATIONAL_ACTION"
        framing = "An ancient agrarian sower"
        if "gieo" in t or "vung" in t:
            subject = "striding purposefully across rolling sunlit hills, broad arm swung wide as golden wheat grains catch warm sunset beams in mid-air"
        elif "quỳ" in t or "đất" in t:
            subject = "kneeling reverently in dark fertile soil at twilight, letting warm crumbly loam sift gently between calloused weathered fingers"
        elif "lúa" in t or "đứng" in t:
            subject = "standing quietly amidst tall ripe golden wheat fields at sunset, open hands gently brushing across heavy nodding grain ears in gratitude"
        else:
            subject = "walking along the edge of the furrowed field with a coarse burlap seed sack slung across shoulder, gazing toward the golden horizon"

    else:
        etype = "OBJECT_MACRO"
        framing = "Macro close-up shot of"
        if "hạt" in t or "mầm" in t or "tay" in t:
            subject = "plump golden wheat grains resting inside a weathered calloused palm, illuminated by low-angle golden hour sunlight"
        elif "vệ đường" in t or "dấu chân" in t or "bụi" in t:
            subject = "a hard-packed sunbaked dirt trail with deep wagon ruts and cracked earth crust, bone-dry and impenetrable"
        elif "chim" in t or "sà" in t:
            subject = "glossy black raven feathers gleaming under sunset light as a bird swoops down to snatch exposed grains from dry road crust"
        elif "sỏi" in t or "đá" in t or "nắng" in t:
            subject = "pale rough limestone gravel scattered across parched earth, a frail pale green sprout wilting under intense white heat"
        elif "gai" in t or "bụi" in t:
            subject = "sharp curved thorns on dark woody briar vines, aggressively twisting around a slender green wheat stem"
        elif "lúa" in t or "bông" in t or "trăm" in t:
            subject = "heavy golden wheat ears bowing under weight of hundredfold ripe grains, rich agrarian textures in warm dusk light"
        elif "lưỡi cày" in t or "cày" in t:
            subject = "a heavy forged iron plow blade cutting cleanly through hard earth crust, turning up dark damp fragrant subsoil"
        elif "bình" in t or "nước" in t:
            subject = "a handcrafted terracotta water pitcher pouring a delicate stream of cool well water over newly sprouted green shoots"
        elif "bó lúa" in t or "gặt" in t:
            subject = "a neatly bundled sheaf of ripe golden wheat tied with natural hemp twine, resting against an ancient olive tree trunk"
        else:
            subject = "a solitary green wheat stalk standing tall against warm amber sunset sky, thriving in rich dark loamy soil"

    return etype, framing, subject


# ==============================================================================
# 3. MINH TRIET SONG (Stoic Philosophy Explainer, 260 beats)
# ==============================================================================

def get_explainer_minh_triet_song(b_idx: int, text: str, ch_idx: int) -> Tuple[str, str, str]:
    """Return (explainer_type, framing, subject) for minh_triet_song."""
    t = text.lower()

    if any(k in t for k in ["ba bài tập", "ba bước", "thứ nhất", "thứ hai", "thứ ba", "bước một", "bước hai", "nguyên tắc"]):
        etype = "STEP_ENUMERATION"
        framing = "Sequential philosophical framework displaying"
        if "thứ nhất" in t or "sáng" in t or "gặp" in t:
            subject = "Morning Stoic preparation: 1. Anticipate ungrateful and arrogant people, 2. Remember common humanity, 3. Anchor in moral duty"
        elif "thứ hai" in t or "kiểm soát" in t:
            subject = "The Dichotomy of Control triage: classify every incoming event strictly as within personal will or beyond personal control"
        elif "thứ ba" in t or "tối" in t or "chiêm nghiệm" in t:
            subject = "Evening self-examination: review where actions stumbled, where virtue succeeded, and where peace was preserved"
        else:
            subject = "three timeless Stoic disciplines: the discipline of desire (Amor Fati), discipline of action (justice), and discipline of assent (truth)"

    elif any(k in t for k in ["thay vì", "trái ngược", "khác biệt", "trong khi", "đối đầu", "so với", "hai nửa", "hai bên", "không phải"]):
        etype = "SPLIT_COMPARISON"
        framing = "50/50 split-screen comparison:"
        if "cân" in t or "kiểm soát" in t or "ngoại cảnh" in t:
            subject = "on the left, an anxious soul tormented by fleeting public praise; on the right, a steadfast philosopher grounded in personal integrity"
        elif "lửa" in t or "khó khăn" in t or "nghịch cảnh" in t:
            subject = "on the left, a victim cursing the bitter winter freeze; on the right, a wise Stoic feeding fallen timber to a blazing hearth fire with gratitude"
        elif "pháo đài" in t or "sóng" in t or "thành" in t:
            subject = "on the left, a flimsy wooden shack shattered by stormy waves; on the right, a monumental granite coastal tower standing unshaken"
        elif "hộp sọ" in t or "danh vọng" in t or "memento" in t:
            subject = "on the left, an imperial triumph parade fading into dust; on the right, a quiet ivory skull crowned by an everlasting laurel wreath"
        elif "vũ trụ" in t or "nhỏ bé" in t or "nhìn" in t:
            subject = "on the left, narrow tunnel-vision obsession with petty squabbles; on the right, the cosmic view from above showing Earth as a pale blue dot"
        else:
            subject = "on the left, reactive anger tearing down inner peace; on the right, sovereign rational composure governing all circumstance"

    elif any(k in t for k in ["cơ chế", "khoảng trống", "tâm trí", "não bộ", "cấu trúc", "pháo đài nội tâm", "lắng đọng"]):
        etype = "MECHANISM_CUTAWAY"
        framing = "Philosophical mechanism cutaway diagram illustrating"
        if "pháo đài" in t or "citadel" in t or "thành trì" in t:
            subject = "the Inner Citadel: impenetrable granite ramparts of rational judgment shielding the sacred flame of moral conscience from all external chaos"
        elif "cân" in t or "vòng tròn" in t or "kiểm soát" in t:
            subject = "Epictetus concentric circles of control: the outer dotted boundary of externals versus the inner golden sphere of rational will and choice"
        elif "lắng" in t or "nước" in t or "đục" in t:
            subject = "a transparent glass cylinder of muddy river water settling in stillness until suspended silt rests on bottom and water becomes crystal clear"
        elif "đẽo" in t or "khối đá" in t or "bức tượng" in t:
            subject = "the concept of the uncarved block (Pu): chipping away societal vanity and greedy impulses to reveal original pure noble human character"
        else:
            subject = "the cognitive reframing mechanism: separating raw sensory impressions from voluntary value judgments to prevent emotional suffering"

    elif any(k in t for k in ["khiến cho", "dẫn đến", "hậu quả", "bắt nguồn", "kết quả", "tạo nên", "rèn luyện"]):
        etype = "CAUSE_EFFECT_DIAGRAM"
        framing = "Cause-and-effect flowchart diagram demonstrating"
        if "amor fati" in t or "số phận" in t or "yêu" in t:
            subject = "how loving whatever fate provides transforms every obstacle into fuel for courage, wisdom, justice, and temperance"
        elif "danh vọng" in t or "hư ảo" in t or "hao mòn" in t:
            subject = "how pursuing external validation surrenders inner sovereignty to strangers, while self-anchored virtue creates unshakeable freedom"
        elif "memento mori" in t or "chết" in t or "ngắn ngủi" in t:
            subject = "how regular awareness of mortality dissolves superficial grievances and elevates every present moment into sacred precious reality"
        else:
            subject = "how consistent athletic mental discipline builds a fortress of resilience capable of withstanding plague, war, and betrayal"

    elif any(k in t for k in ["Marcus Aurelius", "hoàng đế", "bước ra", "ngồi bên", "đứng nhìn"]) and b_idx % 5 == 0:
        etype = "SITUATIONAL_ACTION"
        framing = "Roman Emperor Marcus Aurelius"
        if "viết" in t or "lều" in t or "nến" in t:
            subject = "seated at a scarred oak campaign desk in military tent at the freezing frontier, writing Meditations by tallow candlelight in deep composure"
        elif "sớm" in t or "bình minh" in t or "bước" in t:
            subject = "stepping out of military tent into crisp snowy dawn, looking across mist-covered river with a calm gentle smile, ready for daily duty"
        elif "nhìn" in t or "đứng" in t:
            subject = "standing quietly on a high stone terrace in imperial armor cloak, gazing out at vast winter landscape in serene philosophical stillness"
        else:
            subject = "holding an unrolled papyrus scroll in hand by the warmth of a military camp brazier, reflecting peacefully on the brotherhood of mankind"

    else:
        etype = "OBJECT_MACRO"
        framing = "Macro close-up shot of"
        if "nến" in t or "bàn" in t or "sổ" in t:
            subject = "a flickering tallow candle illuminating an open leather-bound journal and reed pen on rough Roman campaign desk, dark chiaroscuro lighting"
        elif "cân" in t or "chiếc cân" in t:
            subject = "an ancient brass balance scale: one pan weighed down by stormy rain clouds, the other holding an unwavering golden flame"
        elif "lửa" in t or "lò sưởi" in t or "tro" in t:
            subject = "a blazing stone hearth fire consuming dry dead oak branches, turning rough wood into brilliant white heat and glowing red embers"
        elif "pháo đài" in t or "tháp" in t or "đá" in t:
            subject = "a monumental ancient granite coastal watchtower standing motionless while thunderous ocean waves shatter in white foam at base"
        elif "hộp sọ" in t or "đồng hồ" in t or "cát" in t:
            subject = "a delicately carved ivory skull resting beside a bronze hourglass with fine black sand trickling steadily through its glass neck"
        elif "đá cẩm thạch" in t or "tượng" in t or "đục" in t:
            subject = "a rough block of white Carrara marble with sculptor iron chisel and wooden mallet resting on freshly carved stone shavings"
        elif "sông" in t or "nước" in t or "băng" in t:
            subject = "a clear glass vessel filled with pure mountain spring water sitting on dark slate, completely still with not a single ripple"
        elif "vũ trụ" in t or "sao" in t or "hành tinh" in t:
            subject = "an antique brass armillary sphere with concentric rings rotating around a polished lapis lazuli Earth under starlight"
        elif "đe" in t or "búa" in t or "rèn" in t:
            subject = "heavy forged steel blacksmith tongs gripping glowing red-hot iron on an anvil, hammer sparks scattering into shadow"
        elif "vòng nguyệt quế" in t or "ấn tín" in t:
            subject = "an imperial Roman bronze signet ring and a withered laurel wreath resting on aged vellum scroll in warm sidelight"
        else:
            subject = "a weathered classical marble bust of a Stoic philosopher in dramatic side lighting, gaze steady and peaceful against dark slate"

    return etype, framing, subject


# ==============================================================================
# 4. TAM TINH DEM (Nocturnal Contemplation Explainer, 260 beats)
# ==============================================================================

def get_explainer_tam_tinh_dem(b_idx: int, text: str, ch_idx: int) -> Tuple[str, str, str]:
    """Return (explainer_type, framing, subject) for tam_tinh_dem."""
    t = text.lower()

    if any(k in t for k in ["ba lời", "ba bước", "ba điều", "thứ nhất", "thứ hai", "thứ ba", "lời vỗ về", "trước khi ngủ"]):
        etype = "STEP_ENUMERATION"
        framing = "Gentle nocturnal three-step progression displaying"
        if "thứ nhất" in t or "cố gắng" in t:
            subject = "First bedtime affirmation: You have tried your very best today, and your sincere effort is more than enough"
        elif "thứ hai" in t or "ngày mai" in t or "trang mới" in t:
            subject = "Second bedtime affirmation: Tomorrow is a completely blank fresh page, untainted by any mistakes of yesterday"
        elif "thứ ba" in t or "bình yên" in t or "xứng đáng" in t:
            subject = "Third bedtime affirmation: You are unconditionally worthy of gentle rest, deep healing, and quiet peace tonight"
        else:
            subject = "three comforting bedtime affirmations resting like smooth polished river stones in warm bedside lamplight"

    elif any(k in t for k in ["thay vì", "trái ngược", "khác biệt", "trong khi", "đối đầu", "so với", "hai nửa", "một bên", "không phải"]):
        etype = "SPLIT_COMPARISON"
        framing = "50/50 split-screen comparison:"
        if "phố" in t or "ồn ào" in t or "đêm" in t:
            subject = "on the left, a crowded glaring daytime street filled with frantic rushing traffic; on the right, a quiet midnight bedroom washed in soft blue moonlight"
        elif "mặt nạ" in t or "cười" in t:
            subject = "on the left, wearing a rigid polite smiling mask in a corporate crowd; on the right, an authentic relaxed face at home in soft warm pajamas"
        elif "chèo" in t or "thuyền" in t or "dòng nước" in t:
            subject = "on the left, an exhausted rower straining against violent rapids; on the right, a small wooden boat drifting peacefully under benevolent stars"
        elif "điện thoại" in t or "màn hình" in t or "so sánh" in t:
            subject = "on the left, a smartphone screen flashing endless bright comparison feeds; on the right, an open window revealing deep peaceful starry skies"
        elif "cây" in t or "mùa đông" in t or "nghỉ" in t:
            subject = "on the left, an exhausted summer branch pushing premature leaves; on the right, a dormant winter tree saving vital sap in deep roots"
        elif "cô đơn" in t or "một mình" in t:
            subject = "on the left, feeling painfully alienated in a loud crowded room; on the right, savoring rich comforting sanctuary in solitary reading nook"
        else:
            subject = "on the left, harsh late-night self-criticism churning over flaws; on the right, gentle unconditional self-compassion wrapping soul in warmth"

    elif any(k in t for k in ["cơ chế", "tâm trí", "não bộ", "sinh học", "hệ thần kinh", "tầng sâu", "buông xuôi"]):
        etype = "MECHANISM_CUTAWAY"
        framing = "Nocturnal restorative cutaway diagram illustrating"
        if "ngủ" in t or "sóng não" in t or "phục hồi" in t:
            subject = "slow-wave delta sleep architecture: gentle rhythmic neural oscillations clearing cellular metabolic waste and restoring emotional stability"
        elif "mặt nạ" in t or "vai diễn" in t:
            subject = "the psychological energy expenditure of maintaining social facades versus the immediate somatic relief of unmasking in private safety"
        elif "ấm" in t or "trà" in t or "nhiệt" in t:
            subject = "the neurobiological soothing effect of warm chamomile tea: thermal receptor activation triggering oxytocin release and downregulating stress"
        elif "buông" in t or "thả lỏng" in t:
            subject = "the somatic muscular release: tension dissolving from jaw, neck, and shoulders like knotting threads untangling into straight silk"
        else:
            subject = "the neurological transition from daytime hyper-vigilance into safe parasympathetic ease as darkness envelops the home"

    elif any(k in t for k in ["khiến cho", "dẫn đến", "hậu quả", "bắt nguồn", "kết quả", "tạo nên", "mang theo"]):
        etype = "CAUSE_EFFECT_DIAGRAM"
        framing = "Cause-and-effect flowchart diagram demonstrating"
        if "nghỉ ngơi" in t or "tạm dừng" in t:
            subject = "how honoring periods of fallow winter stillness restores deep subterranean vitality, enabling radiant spring growth"
        elif "so sánh" in t or "chậm" in t:
            subject = "how disconnecting from digital comparison feeds eliminates toxic feelings of falling behind, restoring personal timeline pacing"
        elif "tha thứ" in t or "quá khứ" in t:
            subject = "how forgiving past clumsy mistakes immediately lifts the heavy emotional backpack, liberating energy for peaceful sleep"
        else:
            subject = "how small deliberate nighttime rituals of warmth and kindness signal absolute safety to the brain, inviting deep healing rest"

    elif any(k in t for k in ["bạn ngồi", "bước chân", "khép nhẹ", "ngồi lại", "uống một", "kéo chăn", "chìm vào"]) and b_idx % 5 == 0:
        etype = "SITUATIONAL_ACTION"
        framing = "A weary dreamer"
        if "trà" in t or "uống" in t or "tách" in t:
            subject = "sitting curled up in a plush armchair, cradling a steaming ceramic mug of chamomile tea in both palms with a gentle grateful smile"
        elif "chăn" in t or "gối" in t or "nằm" in t:
            subject = "pulling a soft thick wool quilt up over shoulders in cozy bed, resting head onto a plush pillow as moonlight washes over room"
        elif "cửa sổ" in t or "nhìn" in t or "đêm" in t:
            subject = "standing quietly by an apartment window in soft pajamas, looking out at quiet sleeping city roofs under glittering starlight"
        else:
            subject = "resting comfortably with eyes softly closed, listening to gentle night wind rustling leaves outside, breathing in deep rhythmic calm"

    else:
        etype = "OBJECT_MACRO"
        framing = "Macro close-up shot of"
        if "đồng hồ" in t or "tích tắc" in t:
            subject = "an antique brass wall clock with pendulum swinging gently in warm golden lamplight against dark midnight blue wallpaper"
        elif "mặt nạ" in t or "bàn" in t:
            subject = "a delicate white porcelain smiling theatrical mask resting face-up on a rustic wooden nightstand beside a warm glowing amber lamp"
        elif "thuyền" in t or "sông" in t or "nước" in t:
            subject = "a small weathered wooden rowboat with oars resting inside, drifting peacefully on a glassy dark river reflecting Milky Way constellations"
        elif "điện thoại" in t or "màn hình" in t:
            subject = "a black smartphone lying face-down on dark walnut nightstand, screen completely dark and inactive beside an open book"
        elif "cây" in t or "mùa đông" in t or "tuyết" in t:
            subject = "a solitary bare winter deciduous tree silhouette standing quietly in powdery snow beneath a luminous silver crescent moon"
        elif "chăn" in t or "ghế" in t:
            subject = "a thick chunky cable-knit wool blanket folded across a cozy armchair beside a small glowing reading lamp"
        elif "thư" in t or "hộp" in t or "kỷ niệm" in t:
            subject = "an aged cedar keepsake memory box holding gently folded handwritten letters and fragrant sprigs of dried lavender"
        elif "trà" in t or "khói" in t or "tách" in t:
            subject = "a steaming glazed ceramic mug of chamomile tea, delicate curls of fragrant steam catching amber lamplight against midnight window"
        elif "sỏi" in t or "đá" in t:
            subject = "three smooth polished river pebbles resting on a wooden bedside table, warm natural stone textures illuminated by candle glow"
        elif "gối" in t or "giường" in t:
            subject = "a plush white linen pillow bathed in cool silver moonlight through lace curtains, inviting soft restorative slumber"
        else:
            subject = "a warm glowing bedside incandescent lamp casting a gentle circular pool of golden light across an aged pine nightstand"

    return etype, framing, subject


# ==============================================================================
# 5. THUONG CHO KHEO (Empathetic Psychology Explainer, 255 beats)
# ==============================================================================

def get_explainer_thuong_cho_kheo(b_idx: int, text: str, ch_idx: int) -> Tuple[str, str, str]:
    """Return (explainer_type, framing, subject) for thuong_cho_kheo."""
    t = text.lower()

    if any(k in t for k in ["ba bước", "ba điều", "ba bài học", "thứ nhất", "thứ hai", "thứ ba", "quy trình", "nghệ thuật"]):
        etype = "STEP_ENUMERATION"
        framing = "Three-step empathetic communication sequence displaying"
        if "thứ nhất" in t or "dừng" in t or "thở" in t:
            subject = "Step one: pause internal defensive counter-arguments and take one slow grounding breath before reacting"
        elif "thứ hai" in t or "công nhận" in t or "cảm xúc" in t:
            subject = "Step two: mirror and validate the partner underlying emotional pain rather than disputing surface factual details"
        elif "thứ ba" in t or "câu hỏi" in t or "cầu nối" in t:
            subject = "Step three: ask gentle open-ended bridge questions that invite deeper vulnerability and mutual reconnection"
        else:
            subject = "three vital relational stages: dropping mental armor, providing undivided presence, and repairing emotional ruptures"

    elif any(k in t for k in ["thay vì", "trái ngược", "khác biệt", "trong khi", "đối đầu", "so với", "hai nửa", "hai người", "hai góc nhìn"]):
        etype = "SPLIT_COMPARISON"
        framing = "50/50 split-screen comparison:"
        if "lời khuyên" in t or "sửa" in t or "nước mắt" in t:
            subject = "on the left, an impatient partner pushing a rigid analytical checklist; on the right, a loving partner sitting quietly holding space for tears"
        elif "bào chữa" in t or "tòa án" in t or "đúng sai" in t:
            subject = "on the left, a tense mind cross-examining words like an aggressive lawyer; on the right, an open heart listening for unspoken sorrow"
        elif "điện thoại" in t or "màn hình" in t:
            subject = "on the left, two partners staring into separate glowing screens at dinner; on the right, two partners looking warmly into each other eyes"
        elif "kính" in t or "tường" in t:
            subject = "on the left, an invisible thick glass wall separating two distant people; on the right, a gentle hand reaching across table to bridge divide"
        elif "góc nhìn" in t or "lăng kính" in t:
            subject = "on the left, a heated clash over who possesses absolute objective truth; on the right, mutual validation that both subjective realities are real"
        else:
            subject = "on the left, escalating defensive aggression driving loved ones apart; on the right, empathetic validation de-escalating conflict into trust"

    elif any(k in t for k in ["cơ chế", "não bộ", "tâm lý", "gắn kết", "hệ thần kinh", "tầng sâu", "phản xạ"]):
        etype = "MECHANISM_CUTAWAY"
        framing = "Relational psychological cutaway diagram illustrating"
        if "gắn kết" in t or "lo âu" in t or "né tránh" in t:
            subject = "attachment styles: the anxious reaching hand longing for reassurance versus the avoidant shell retreating into defensive silence"
        elif "nghe" in t or "thấu" in t or "sóng âm" in t:
            subject = "acoustic hearing versus cardiac listening: soundwaves merely striking ear drums versus emotional mirroring circuits lighting up in empathy"
        elif "tảng băng" in t or "bề mặt" in t:
            subject = "the communication iceberg model: angry surface words representing ten percent above water while ninety percent submerged needs are unseen"
        elif "gương" in t or "phản chiếu" in t:
            subject = "the emotional mirroring resonator effect: calmly reflecting back spoken feelings immediately downregulating amygdala alarm in speaker brain"
        else:
            subject = "the neurobiology of relational attunement: mutual eye contact and soft vocal cadence releasing oxytocin and soothing threat reflexes"

    elif any(k in t for k in ["khiến cho", "dẫn đến", "hậu quả", "bắt nguồn", "kết quả", "tạo nên", "đổ thêm dầu"]):
        etype = "CAUSE_EFFECT_DIAGRAM"
        framing = "Cause-and-effect flowchart diagram demonstrating"
        if "lời khuyên" in t or "sớm" in t or "cô lập" in t:
            subject = "how offering premature unsolicited advice makes the hurt partner feel invalidated and unheard, driving them into deeper defensive isolation"
        elif "thấu cảm" in t or "chữa lành" in t:
            subject = "how validating emotional reality without requiring agreement immediately dissolves defensive walls and opens the door to collaborative solutions"
        elif "ranh giới" in t or "từ chối" in t or "bảo vệ" in t:
            subject = "how establishing clear loving personal boundaries prevents caregiver burnout and protects long-term relational generosity"
        else:
            subject = "how winning a factual intellectual debate usually results in losing the emotional relationship, destroying genuine intimacy"

    elif any(k in t for k in ["hai người", "ngồi", "bàn tay", "nhìn nhau", "bước lại", "chạm vào"]) and b_idx % 5 == 0:
        etype = "SITUATIONAL_ACTION"
        framing = "Two partners in intimate conversation"
        if "tay" in t or "chạm" in t or "nắm" in t:
            subject = "one partner gently reaching across the wooden dining table to place a warm open palm over the other trembling clenched fingers with deep love"
        elif "nhìn" in t or "mắt" in t or "ngồi" in t:
            subject = "sitting facing each other on a comfortable sofa in soft morning windowlight, making steady compassionate eye contact without interruption"
        elif "cơm" in t or "bàn" in t:
            subject = "seated across from each other at an oak dining table, listening with quiet tilted heads and soft relaxed expressions in warm ambient light"
        else:
            subject = "standing close together in quiet hallway light, sharing a tender embracing moment of mutual reconciliation and heartfelt relief"

    else:
        etype = "OBJECT_MACRO"
        framing = "Macro close-up shot of"
        if "bát canh" in t or "mâm cơm" in t or "khói" in t:
            subject = "a ceramic soup bowl sitting untouched on a dark polished oak dining table between two distant place settings, delicate broth cooling"
        elif "kính" in t or "tường" in t:
            subject = "a thick vertical pane of transparent glass slicing down the center of dining table, physically dividing two people sitting inches apart"
        elif "điện thoại" in t or "màn hình" in t:
            subject = "a black smartphone resting face-down on a dark wooden table beside two steaming ceramic tea mugs, screen completely inactive"
        elif "sổ" in t or "bút" in t or "ghi" in t:
            subject = "an open notepad with an analytical checklist and red pen being pushed across table toward someone who is visibly weeping"
        elif "búa" in t or "tòa" in t:
            subject = "a miniature polished bronze judicial gavel resting on dark wood, symbolizing the internal courtroom cross-examination of partner words"
        elif "tay" in t or "ngón tay" in t or "run" in t:
            subject = "trembling pale fingers resting on polished dining table wood, knuckles slightly tense, illuminated by warm domestic sidelight"
        elif "lăng kính" in t or "ánh sáng" in t:
            subject = "two distinct optical glass prisms splitting a single beam of warm sunlight into two harmoniously overlapping colorful rainbows"
        elif "chìa khóa" in t or "cửa" in t:
            subject = "an antique brass key turning smoothly inside an intricate lock on a heavy solid oak door, door beginning to click open to warm hallway"
        elif "ô" in t or "mưa" in t:
            subject = "a delicate velvet umbrella shielding a fragile flowering potted plant from heavy rain, raindrops rolling harmlessly off fabric"
        elif "bát vỡ" in t or "kintsugi" in t or "hàn gắn" in t:
            subject = "a shattered antique celadon tea cup lovingly reassembled with shimmering veins of pure twenty-four karat gold kintsugi lacquer lines"
        elif "tách trà" in t or "hai tách" in t:
            subject = "two steaming handcrafted ceramic tea mugs sitting side by side on a clean wooden table, gentle curls of steam mingling in morning light"
        else:
            subject = "two comfortable wooden dining chairs angled warmly forty-five degrees toward each other in a cozy sunlit room, inviting open connection"

    return etype, framing, subject
