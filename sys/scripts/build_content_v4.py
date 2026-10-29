import json, os, sys

def build_content():
    content_dir = 'sys/runs/survivorship-bias-16x9/revisions/content/3'
    os.makedirs(content_dir, exist_ok=True)
    
    with open('sys/runs/survivorship-bias-16x9/revisions/content/2/content.json') as f:
        c = json.load(f)
        
    with open('sys/runs/survivorship-bias-16x9/briefs/3.json') as f:
        b = json.load(f)
        
    c['brief_revision'] = 3
    c['brief_hash'] = '66e64596660a27f1f74347a44d0d8445b4a46d022fc280110e97b409dfa94f4c'
    c['required_points'] = [rp['text'] for rp in b['required_points']]
    
    # Update SC01
    s1 = c['scenes'][0]
    s1['title'] = 'Cơn sốt mở quán F&B và ảo tưởng thành công'
    s1['purpose'] = 'Mở bài bằng cú tát nhận thức: bắt chước người thành công là cách nhanh nhất để bạn trắng tay qua cơn sốt mở quán F&B nhượng quyền'
    s1['narration'] = 'Bắt chước người thành công là cách nhanh nhất để bạn trắng tay. Hãy nhìn vào những cơn sốt mở quán gần đây: một người đi đầu tạo ra trào lưu, khoe doanh thu vài chục triệu mỗi ngày và bán nhượng quyền khắp nơi. Hàng nghìn người trẻ thấy vậy, vội rút sạch tiền tiết kiệm, thậm chí vay mượn để làm theo từng bước: cũng thuê mặt bằng đắt đỏ, cũng mua máy móc hiện đại, cũng làm đúng công thức. Nhưng chỉ ba tháng sau khi trào lưu nguội lạnh, người đi đầu đã kịp đút túi tiền tỷ, còn hàng nghìn người mở theo chỉ còn lại đống máy móc sắt vụn và một khoản nợ ngập đầu.'
    
    s1_images = [
        ('SC01_I1', 'Bắt chước người thành công là cách', 'Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a shining golden trophy cup tilted over on a stone pedestal, spilling out empty round tokens.', 'still_life', 'punch_in'),
        ('SC01_I2', 'nhanh nhất để bạn trắng tay.', 'Flat 2D close-up on an apricot-peach (#F2B88B) field: an open empty wallet held by white stickman hands with cobwebs and zero money inside.', 'still_life', 'zoom_out'),
        ('SC01_I3', 'Hãy nhìn vào những cơn sốt mở quán gần đây:', 'Flat 2D orthographic storefront on a pale ice-blue (#CBE0E0) field: a trendy beverage cafe with bright neon signs and a long winding queue of white-head doodle stickmen.', 'full_scene', 'pan_right'),
        ('SC01_I4', 'một người đi đầu tạo ra trào lưu, khoe doanh thu vài chục triệu mỗi ngày', 'Flat 2D frame on a warm paper-cream (#F8F0DC) field: a smiling founder stickman in a blue shirt holds a glowing smartphone showing DOANH THU 50 TRIỆU NGÀY.', 'full_scene', 'punch_in'),
        ('SC01_I5', 'và bán nhượng quyền khắp nơi.', 'Flat 2D close-up on a soft sage-green (#93A88C) field: five franchise contract certificates stamped with red wax seals spreading out on a wooden counter.', 'still_life', 'zoom_out'),
        ('SC01_I6', 'Hàng nghìn người trẻ thấy vậy, vội rút sạch tiền tiết kiệm,', 'Flat 2D close-up on an apricot-peach (#F2B88B) field: a pink ceramic piggy bank cracked open beside neat stacks of hard-earned paper banknotes.', 'still_life', 'hold'),
        ('SC01_I7', 'thậm chí vay mượn để làm theo từng bước:', 'Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a commercial loan agreement paper stamped with bold red ink VAY VỐN beside an ink pen.', 'still_life', 'zoom_in'),
        ('SC01_I8', 'cũng thuê mặt bằng đắt đỏ,', 'Flat 2D orthographic corner on a slate-navy (#2E4361) street stage: a city storefront window hung with a bold white sign CHO THUÊ MẶT BẰNG.', 'full_scene', 'pan_left'),
        ('SC01_I9', 'cũng mua máy móc hiện đại, cũng làm đúng công thức.', 'Flat 2D close-up on a pale ice-blue (#CBE0E0) field: three shiny steel commercial blender machines and a ring-bound recipe book open with colored drink charts.', 'still_life', 'zoom_out'),
        ('SC01_I10', 'Nhưng chỉ ba tháng sau khi trào lưu nguội lạnh,', 'Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a three-month calendar page tearing off beside a large melting blue ice block.', 'still_life', 'punch_in'),
        ('SC01_I11', 'người đi đầu đã kịp đút túi tiền tỷ,', 'Flat 2D orthographic frame on a soft sage-green (#93A88C) field: the founder stickman walking away smiling with two heavy brown sacks labeled TIỀN TỶ.', 'full_scene', 'pan_right'),
        ('SC01_I12', 'còn hàng nghìn người mở theo chỉ còn lại đống máy móc sắt vụn và một khoản nợ ngập đầu.', 'Flat 2D orthographic interior on a slate-navy (#2E4361) night stage: the white-head stickman sits with head in hands inside a dark empty cafe beside dusty unplugged machines and debt bills.', 'full_scene', 'zoom_out'),
    ]
    
    s1['images'] = []
    s1['beats'] = []
    for img_id, quote, desc, shot_type, effect in s1_images:
        assert quote in s1['narration'], f"Quote not in s1 narration: {quote}"
        s1['images'].append({
            'id': img_id,
            'description': desc,
            'character_ids': ['CH01'] if shot_type == 'full_scene' else [],
            'based_on': None,
            'preserve': '',
            'change': desc,
            'reason': 'Show the concrete object, comparison, or action at its spoken anchor.',
            'visible_text': [],
            'kind': 'scene',
            'shot_type': shot_type,
            'has_character': shot_type == 'full_scene',
            'explanation': {
                'quote': quote,
                'relation': 'context',
                'source_terms': [quote.split()[-1]],
                'visual_terms': [desc[:40]]
            }
        })
        s1['beats'].append({
            'id': img_id.replace('_I', '_B'),
            'image_id': img_id,
            'purpose': s1['purpose'],
            'anchor': {'vi': {'quote': quote, 'occurrence': 1}},
            'effect': effect,
            'focus': {'x': 0.5, 'y': 0.5}
        })
        
    # Update SC02
    s2 = c['scenes'][1]
    s2['title'] = 'Bóc trần quy luật bán xẻng cho người đào vàng'
    s2['purpose'] = 'Bóc trần quy luật bán xẻng cho người đào vàng và gọi tên Bẫy Người Sống Sót'
    s2['narration'] = 'Tại sao làm y hệt người ta mà bạn lại phá sản? Bởi vì bạn chỉ nhìn thấy ly nước và dòng người xếp hàng, mà mù tịt trước nguồn tiền thật sự: người ta giàu lên nhờ bán xẻng cho người đào vàng, bán công thức cho những kẻ đến sau, chứ không phải nhờ bán từng ly nước khi thị trường đã bão hòa. Bạn không thua vì kém. Bạn thua vì chỉ được xem một nửa câu chuyện mà người ta muốn cho bạn thấy. Cái bẫy đó mang tên: Bẫy Người Sống Sót. Hiểu nó, bạn sẽ biết lúc nào nên học hỏi, và lúc nào phải dừng tay trước khi mất tiền oan.'
    
    s2_images = [
        ('SC02_I1', 'Tại sao làm y hệt người ta mà bạn lại phá sản?', 'Flat 2D orthographic card on an apricot-peach (#F2B88B) field: a large red question mark hovering above a broken metal cash register box.', 'still_life', 'punch_in'),
        ('SC02_I2', 'Bởi vì bạn chỉ nhìn thấy ly nước và dòng người xếp hàng,', 'Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a colorful plastic cup with black tapioca pearls beside silhouettes of a dense crowd.', 'still_life', 'zoom_out'),
        ('SC02_I3', 'mà mù tịt trước nguồn tiền thật sự:', 'Flat 2D orthographic frame on a slate-navy (#2E4361) field: a heavy black curtain pulled shut across a mysterious glowing iron vault door.', 'still_life', 'hold'),
        ('SC02_I4', 'người ta giàu lên nhờ bán xẻng cho người đào vàng,', 'Flat 2D orthographic card on a soft sage-green (#93A88C) field: an entrepreneur stickman selling shiny iron shovels labeled BÁN XẺNG to miners digging in mud.', 'full_scene', 'pan_right'),
        ('SC02_I5', 'bán công thức cho những kẻ đến sau,', 'Flat 2D close-up on a warm paper-cream (#F8F0DC) field: stacks of packaged franchise training booklets and stamped paper diplomas sold across a high counter.', 'still_life', 'punch_in'),
        ('SC02_I6', 'chứ không phải nhờ bán từng ly nước khi thị trường đã bão hòa.', 'Flat 2D diagram on a stark pure-white (#FFFFFF) canvas: a sharp downward red graph line with hundreds of identical cup icons crowding the bottom zone.', 'visual_diagram', 'zoom_out'),
        ('SC02_I7', 'Bạn không thua vì kém. Bạn thua vì chỉ được xem một nửa câu chuyện mà người ta muốn cho bạn thấy.', 'Flat 2D diagram on a pale ice-blue (#CBE0E0) field: a round pie chart sliced in half with one bright yellow half labeled BỀ NỔI and one black half labeled SỰ THẬT.', 'visual_diagram', 'hold'),
        ('SC02_I8', 'Cái bẫy đó mang tên: Bẫy Người Sống Sót.', 'Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a bold toothed steel bear trap enclosing a golden plaque that reads BẪY NGƯỜI SỐNG SÓT.', 'still_life', 'punch_in'),
        ('SC02_I9', 'Hiểu nó, bạn sẽ biết lúc nào nên học hỏi, và lúc nào phải dừng tay trước khi mất tiền oan.', 'Flat 2D orthographic stage on an apricot-peach (#F2B88B) field: the white-head stickman in a blue shirt holds up an open palm stopping before an edge, with a glowing lightbulb overhead.', 'full_scene', 'zoom_out'),
    ]
    
    s2['images'] = []
    s2['beats'] = []
    for img_id, quote, desc, shot_type, effect in s2_images:
        assert quote in s2['narration'], f"Quote not in s2 narration: {quote}"
        s2['images'].append({
            'id': img_id,
            'description': desc,
            'character_ids': ['CH01'] if shot_type == 'full_scene' else [],
            'based_on': None,
            'preserve': '',
            'change': desc,
            'reason': 'Show the concrete object, comparison, or action at its spoken anchor.',
            'visible_text': [],
            'kind': 'scene',
            'shot_type': shot_type,
            'has_character': shot_type == 'full_scene',
            'explanation': {
                'quote': quote,
                'relation': 'context',
                'source_terms': [quote.split()[-1]],
                'visual_terms': [desc[:40]]
            }
        })
        s2['beats'].append({
            'id': img_id.replace('_I', '_B'),
            'image_id': img_id,
            'purpose': s2['purpose'],
            'anchor': {'vi': {'quote': quote, 'occurrence': 1}},
            'effect': effect,
            'focus': {'x': 0.5, 'y': 0.5}
        })
        
    # Update SC04
    s4 = c['scenes'][3]
    s4['title'] = 'Đánh tráo hệ quả thành nguyên nhân làm giàu'
    s4['purpose'] = 'Bóc tách sai lầm đánh tráo phong cách sống sau khi giàu thành bí quyết làm giàu cho người mới bắt đầu'
    s4['narration'] = 'Cái nguy hiểm nhất của bẫy này: nó khiến ta nhầm phong cách sống thành bí quyết làm giàu. Thấy người giàu đọc hàng chục cuốn sách, thiền định, hay chia sẻ về tư duy an lạc, ta vội tin làm theo là sẽ đổi đời. Nhưng họ thảnh thơi vì họ đã có núi tiền trong tài khoản, chứ việc ngồi thiền không thể biến ai thành triệu phú. Đánh tráo kết quả của người thắng cuộc thành công thức cho người mới bắt đầu là cái bẫy ngọt ngào nhất của truyền thông.'
    
    s4_images = [
        ('SC04_I1', 'Cái nguy hiểm nhất của bẫy này: nó khiến ta nhầm phong cách sống', 'Flat 2D diagram on a stark pure-white (#FFFFFF) canvas: a balance scale weighing a gold luxury watch on one side against a brass key on the other.', 'visual_diagram', 'punch_in'),
        ('SC04_I2', 'thành bí quyết làm giàu. Thấy người giàu đọc hàng chục cuốn sách, thiền định,', 'Flat 2D orthographic stage on a warm paper-cream (#F8F0DC) field: a wealthy stickman in blazer sits in lotus meditation pose beside a stack of fifty books and a golf club.', 'full_scene', 'zoom_out'),
        ('SC04_I3', 'hay chia sẻ về tư duy an lạc, ta vội tin làm theo là sẽ đổi đời.', 'Flat 2D orthographic frame on an apricot-peach (#F2B88B) field: an aspiring stickman in casual shirt sits in identical lotus pose beside an open notebook, waiting expectantly.', 'full_scene', 'hold'),
        ('SC04_I4', 'Nhưng họ thảnh thơi vì họ đã có núi tiền trong tài khoản,', 'Flat 2D orthographic diagram on a soft sage-green (#93A88C) field: a massive bedrock platform made of green banknote stacks and gold ingots supporting the high seat.', 'visual_diagram', 'punch_in'),
        ('SC04_I5', 'chứ việc ngồi thiền không thể biến ai thành triệu phú.', 'Flat 2D close-up on a pale ice-blue (#CBE0E0) field: an empty cloth wallet turned upside down with zero coins falling out and cobwebs inside.', 'still_life', 'zoom_out'),
        ('SC04_I6', 'Đánh tráo kết quả của người thắng cuộc thành công thức cho người mới bắt đầu là cái bẫy ngọt ngào nhất của truyền thông.', 'Flat 2D orthographic stage on a slate-navy (#2E4361) field: a bright television camera projecting a shining halo onto a presenter while a wooden mouse trap lies on the floor.', 'full_scene', 'hold'),
    ]
    
    s4['images'] = []
    s4['beats'] = []
    for img_id, quote, desc, shot_type, effect in s4_images:
        assert quote in s4['narration'], f"Quote not in s4 narration: {quote}"
        s4['images'].append({
            'id': img_id,
            'description': desc,
            'character_ids': ['CH01'] if shot_type == 'full_scene' else [],
            'based_on': None,
            'preserve': '',
            'change': desc,
            'reason': 'Show the concrete object, comparison, or action at its spoken anchor.',
            'visible_text': [],
            'kind': 'scene',
            'shot_type': shot_type,
            'has_character': shot_type == 'full_scene',
            'explanation': {
                'quote': quote,
                'relation': 'context',
                'source_terms': [quote.split()[-1]],
                'visual_terms': [desc[:40]]
            }
        })
        s4['beats'].append({
            'id': img_id.replace('_I', '_B'),
            'image_id': img_id,
            'purpose': s4['purpose'],
            'anchor': {'vi': {'quote': quote, 'occurrence': 1}},
            'effect': effect,
            'focus': {'x': 0.5, 'y': 0.5}
        })

    # Update SC07
    s7 = c['scenes'][6]
    s7['title'] = 'Vết đạn trên cánh vs. Động cơ sống còn ngoài đời thực'
    s7['purpose'] = 'Liên hệ bài toán máy bay với thực tế kinh doanh: mặt bằng đẹp, decor chỉ là vết đạn ở cánh; vốn gồng lỗ 2 năm, ăn đầu sóng mới là động cơ'
    s7['narration'] = 'Quay lại câu chuyện kinh doanh. Mặt bằng đẹp, cách trang trí, công thức pha chế — đó chỉ là vết đạn trên cánh. Ai cũng thấy, ai cũng sao chép được, và chúng không quyết định việc bạn sống hay chết. Động cơ sống còn thực sự là thứ bị giấu nhẹm: vị thế vốn đủ gồng lỗ hai năm, kiếm tiền từ đầu sóng, hay năng lực xử lý rủi ro khi thị trường quay đầu.'
    
    s7_images = [
        ('SC07_I1', 'Quay lại câu chuyện kinh doanh.', 'Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a 1943 military aircraft blueprint drawing transitioning smoothly into a modern cafe store layout.', 'still_life', 'punch_in'),
        ('SC07_I2', 'Mặt bằng đẹp, cách trang trí, công thức pha chế — đó chỉ là vết đạn trên cánh.', 'Flat 2D orthographic diagram on a stark pure-white (#FFFFFF) canvas: a bomber plane wing covered with colorful drink stickers, neon signs, and bullet hole markers.', 'visual_diagram', 'zoom_out'),
        ('SC07_I3', 'Ai cũng thấy, ai cũng sao chép được, và chúng không quyết định việc bạn sống hay chết.', 'Flat 2D orthographic stage on an apricot-peach (#F2B88B) field: three identical copycat stickmen holding identical beverage cups with identical shop aprons.', 'full_scene', 'pan_right'),
        ('SC07_I4', 'Động cơ sống còn thực sự là thứ bị giấu nhẹm:', 'Flat 2D orthographic diagram on a slate-navy (#2E4361) field: the twin bomber plane engines glowing in bold red outline locked behind iron padlocks.', 'visual_diagram', 'punch_in'),
        ('SC07_I5', 'vị thế vốn đủ gồng lỗ hai năm,', 'Flat 2D close-up on a soft sage-green (#93A88C) field: a heavy steel safe labeled VỐN GỒNG LỖ 2 NĂM anchored deep into solid granite bedrock.', 'still_life', 'zoom_out'),
        ('SC07_I6', 'kiếm tiền từ đầu sóng,', 'Flat 2D orthographic frame on a pale ice-blue (#CBE0E0) field: a stickman surfing gracefully on the high crest of an ocean wave, while latecomers swim below.', 'full_scene', 'hold'),
        ('SC07_I7', 'hay năng lực xử lý rủi ro khi thị trường quay đầu.', 'Flat 2D orthographic stage on a warm paper-cream (#F8F0DC) field: the white-head stickman protected under a reinforced steel umbrella shielding against falling thunderbolts.', 'full_scene', 'zoom_out'),
    ]
    
    s7['images'] = []
    s7['beats'] = []
    for img_id, quote, desc, shot_type, effect in s7_images:
        assert quote in s7['narration'], f"Quote not in s7 narration: {quote}"
        s7['images'].append({
            'id': img_id,
            'description': desc,
            'character_ids': ['CH01'] if shot_type == 'full_scene' else [],
            'based_on': None,
            'preserve': '',
            'change': desc,
            'reason': 'Show the concrete object, comparison, or action at its spoken anchor.',
            'visible_text': [],
            'kind': 'scene',
            'shot_type': shot_type,
            'has_character': shot_type == 'full_scene',
            'explanation': {
                'quote': quote,
                'relation': 'context',
                'source_terms': [quote.split()[-1]],
                'visual_terms': [desc[:40]]
            }
        })
        s7['beats'].append({
            'id': img_id.replace('_I', '_B'),
            'image_id': img_id,
            'purpose': s7['purpose'],
            'anchor': {'vi': {'quote': quote, 'occurrence': 1}},
            'effect': effect,
            'focus': {'x': 0.5, 'y': 0.5}
        })

    # Update SC10
    s10 = c['scenes'][9]
    s10['title'] = 'Bước 1: Khảo sát đáy biển (Tìm người vừa sang nhượng)'
    s10['purpose'] = 'Hướng dẫn thực hành Bước 1: Khảo sát đáy biển qua hội nhóm thanh lý và người vừa sang nhượng để tìm chi phí ẩn'
    s10['narration'] = 'Trước mọi quyết định lớn về tiền hay sự nghiệp, hãy làm hai bước. Bước một: đừng nghe lời người đang kiếm được tiền từ nó. Hãy tìm đến các hội nhóm thanh lý, gặp những người vừa phải đóng cửa sang nhượng trong ngành. Mời họ một ly cà phê và hỏi: chi phí ẩn nào đã bóp nghẹt họ? Cú sẩy chân nào đã khiến họ phải bỏ cuộc? Đó mới là những chiếc máy bay dưới đáy biển mà bạn buộc phải thấy.'
    
    s10_images = [
        ('SC10_I1', 'Trước mọi quyết định lớn về tiền hay sự nghiệp, hãy làm hai bước.', 'Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a clean wooden road sign with two directional arrows marked BƯỚC 1 and BƯỚC 2.', 'still_life', 'punch_in'),
        ('SC10_I2', 'Bước một: đừng nghe lời người đang kiếm được tiền từ nó.', 'Flat 2D orthographic frame on an apricot-peach (#F2B88B) field: a smiling salesperson stickman holding a megaphone crossed out with a gentle red diagonal circle.', 'full_scene', 'zoom_out'),
        ('SC10_I3', 'Hãy tìm đến các hội nhóm thanh lý,', 'Flat 2D close-up on a stark pure-white (#FFFFFF) canvas: a vertical smartphone screen showing a forum page header HỘI THANH LÝ ĐỒ NGHỀ & SANG NHƯỢNG.', 'still_life', 'punch_in'),
        ('SC10_I4', 'gặp những người vừa phải đóng cửa sang nhượng trong ngành.', 'Flat 2D orthographic street view on a slate-navy (#2E4361) field: a closed storefront with pulled-down rolling shutter hung with a handwritten banner SANG NHƯỢNG.', 'full_scene', 'pan_right'),
        ('SC10_I5', 'Mời họ một ly cà phê và hỏi:', 'Flat 2D orthographic stage on a warm paper-cream (#F8F0DC) field: two white-head stickmen sitting across a small sidewalk cafe table with two iced coffee glasses, talking candidly.', 'full_scene', 'hold'),
        ('SC10_I6', 'chi phí ẩn nào đã bóp nghẹt họ? Cú sẩy chân nào đã khiến họ phải bỏ cuộc?', 'Flat 2D close-up on a soft sage-green (#93A88C) field: a spiral notepad with handwritten notes listing CHI PHÍ ẨN, TIỀN NHÀ TĂNG, and MÙA MƯA.', 'still_life', 'zoom_in'),
        ('SC10_I7', 'Đó mới là những chiếc máy bay dưới đáy biển mà bạn buộc phải thấy.', 'Flat 2D diagram on a pale ice-blue (#CBE0E0) field: a cross-section of deep ocean water with dark sunken propeller bomber plane silhouettes resting on the sandy floor.', 'visual_diagram', 'zoom_out'),
    ]
    
    s10['images'] = []
    s10['beats'] = []
    for img_id, quote, desc, shot_type, effect in s10_images:
        assert quote in s10['narration'], f"Quote not in s10 narration: {quote}"
        s10['images'].append({
            'id': img_id,
            'description': desc,
            'character_ids': ['CH01'] if shot_type == 'full_scene' else [],
            'based_on': None,
            'preserve': '',
            'change': desc,
            'reason': 'Show the concrete object, comparison, or action at its spoken anchor.',
            'visible_text': [],
            'kind': 'scene',
            'shot_type': shot_type,
            'has_character': shot_type == 'full_scene',
            'explanation': {
                'quote': quote,
                'relation': 'context',
                'source_terms': [quote.split()[-1]],
                'visual_terms': [desc[:40]]
            }
        })
        s10['beats'].append({
            'id': img_id.replace('_I', '_B'),
            'image_id': img_id,
            'purpose': s10['purpose'],
            'anchor': {'vi': {'quote': quote, 'occurrence': 1}},
            'effect': effect,
            'focus': {'x': 0.5, 'y': 0.5}
        })
        
    with open(f'{content_dir}/content.json', 'w') as f:
        json.dump(c, f, indent=2, ensure_ascii=False)
        
    print(f'Successfully built {content_dir}/content.json with 12 scenes.')

if __name__ == '__main__':
    build_content()
