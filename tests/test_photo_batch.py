from copy import deepcopy

from models import PhotoBatchExtraction, PhotoItemExtraction
from photo_pipeline import included_items, merge_adjacent_items, normalize_photo_batch


def test_batch_models_normalize_text_subject_warnings_and_sources():
    result = PhotoBatchExtraction.model_validate({
        'items': [{
            'question_no': '9', 'question': '  1+1=?  ', 'student_answer': None,
            'student_thought': ' 1+1=3 ', 'correct_answer': None,
            'subject': '天文学', 'source_images': [2, '1', 2, 0, -1, 'bad'],
            'confidence_note': ' 字迹较清晰 ', 'warnings': ['', ' 核对等号 '],
        }],
        'warnings': [' 全局核对 '], 'confidence_note': ' 可识别 ',
    })
    item = result.items[0]
    assert isinstance(item, PhotoItemExtraction)
    assert item.question == '1+1=?'
    assert item.student_answer == '' and item.correct_answer == ''
    assert item.subject == '其他'
    assert item.source_images == [1, 2]
    assert item.warnings == ['核对等号']
    assert result.warnings == ['全局核对']


def test_normalize_batch_assigns_stable_numbers_and_filters_invalid_sources():
    payload = {
        'items': [
            {'question_no': 8, 'question': 'A', 'source_images': [1, 7]},
            {'question_no': 8, 'question': 'B', 'source_images': []},
            {'question_no': 2, 'question': 'C', 'source_images': [2]},
        ],
        'warnings': ['核对图片'],
    }
    state = normalize_photo_batch(payload, image_count=2)
    assert [item['question_no'] for item in state['items']] == [1, 2, 3]
    assert state['items'][0]['source_images'] == [1]
    assert state['items'][0]['source_unknown'] is True
    assert state['items'][1]['source_unknown'] is True
    assert state['items'][2]['source_unknown'] is False
    assert all(item['included'] for item in state['items'])
    assert state['warnings'] == ['核对图片']


def test_normalize_batch_keeps_one_editable_empty_item_when_model_returns_none():
    state = normalize_photo_batch({'items': []}, image_count=3)
    assert len(state['items']) == 1
    assert state['items'][0]['question_no'] == 1
    assert state['items'][0]['question'] == ''
    assert state['items'][0]['source_unknown'] is True
    assert '没有拆分出题目' in state['warnings'][0]


def test_merge_is_non_mutating_consumes_next_item_and_never_duplicates_text():
    original = normalize_photo_batch({'items': [
        {'question': 'A', 'student_answer': '答A', 'student_thought': '思A',
         'correct_answer': '正A', 'source_images': [1]},
        {'question': 'B', 'student_answer': '答B', 'student_thought': '思B',
         'correct_answer': '正B', 'source_images': [2]},
    ]}, image_count=2)['items']
    before = deepcopy(original)
    merged = merge_adjacent_items(original, 0)
    assert original == before
    assert merged[0]['question'] == 'A\nB'
    assert merged[0]['student_answer'] == '答A\n答B'
    assert merged[0]['student_thought'] == '思A\n思B'
    assert merged[0]['correct_answer'] == '正A\n正B'
    assert merged[0]['source_images'] == [1, 2]
    assert merged[1]['included'] is False
    assert merged[1]['merged_into'] == 1
    assert merge_adjacent_items(merged, 0) == merged


def test_merge_preserves_unknown_provenance_and_can_continue_with_third_item():
    items = normalize_photo_batch({'items': [
        {'question': 'A', 'source_images': []},
        {'question': 'B', 'source_images': [2]},
        {'question': 'C', 'source_images': [3]},
    ]}, image_count=3)['items']
    first = merge_adjacent_items(items, 0)
    assert first[0]['source_images'] == [2]
    assert first[0]['source_unknown'] is True
    second = merge_adjacent_items(first, 0)
    assert second[0]['question'] == 'A\nB\nC'
    assert second[0]['source_images'] == [2, 3]
    assert second[0]['source_unknown'] is True
    assert [item['merged_into'] for item in second[1:]] == [1, 1]


def test_included_items_excludes_consumed_disabled_and_blank_questions():
    items = normalize_photo_batch({'items': [
        {'question': '保留'}, {'question': '排除'}, {'question': ''}, {'question': '被合并'},
    ]}, image_count=1)['items']
    items[1]['included'] = False
    items[3]['merged_into'] = 1
    items[3]['included'] = True
    selected = included_items(items)
    assert [item['question'] for item in selected] == ['保留']


def test_normalize_does_not_mutate_caller_payload():
    payload = {'items': [{'question': '题', 'source_images': [1]}]}
    before = deepcopy(payload)
    normalize_photo_batch(payload, 1)
    assert payload == before
