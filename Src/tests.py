import pytest
from image_processor import ImageProcessor
from PIL import Image
import tempfile
import os
from unittest.mock import patch

@pytest.fixture
def processor():
    return ImageProcessor()

@pytest.fixture
def temp_image():
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color='red')
        img.save(tmp.name)
    yield tmp.name
    os.unlink(tmp.name)

def test_load_image_success(processor, temp_image):
    img = processor.load_image(temp_image)
    assert isinstance(img, Image.Image)
    assert img.size == (100, 100)
    assert img.mode == 'RGB'

def test_load_image_file_not_found(processor):
    with pytest.raises(FileNotFoundError):
        processor.load_image('non_existent_file.jpg')

def test_get_info(processor, temp_image):
    img = processor.load_image(temp_image)
    info = processor.get_info(img)
    assert info['width'] == 100
    assert info['height'] == 100
    assert info['format'] == 'PNG'
    assert info['mode'] == 'RGB'

def test_resize(processor, temp_image):
    img = processor.load_image(temp_image)
    resized = processor.resize(img, (50, 50))
    assert resized.size == (50, 50)

@patch('logging.info')  
def test_process_with_filters(mock_log, processor, temp_image):
    img = processor.load_image(temp_image)
    processed = processor.process(img, (80, 80), apply_sharpen=True, apply_contour=True)
    assert processed.size == (80, 80)
    assert mock_log.call_count >= 3  

def test_save(processor, temp_image):
    img = processor.load_image(temp_image)
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_out:
        processor.save(img, tmp_out.name)
    assert os.path.exists(tmp_out.name)
    saved_img = Image.open(tmp_out.name)
    assert saved_img.format == 'JPEG'
    saved_img.close()  
    os.unlink(tmp_out.name)