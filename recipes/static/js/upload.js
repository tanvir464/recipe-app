document.addEventListener('DOMContentLoaded', function() {
    const contentSections = document.getElementById('contentSections');
    const addTextBtn = document.getElementById('addTextBtn');
    const addImageBtn = document.getElementById('addImageBtn');
    
    let sectionCounter = 0;

    function createContentSection(type) {
        const section = document.createElement('div');
        section.className = 'content-section mb-4';
        section.innerHTML = `
            <button type="button" class="remove-btn">&times;</button>
            ${type === 'text' 
                ? `<textarea class="form-control" name="text_content[]" rows="4" placeholder="Enter your recipe instructions here" required></textarea>`
                : `
                    <input type="file" class="form-control image-input" name="image_content[]" accept="image/*" required>
                    <div class="d-flex justify-content-center mt-2">
                        <img src="#" alt="Image Preview" class="img-preview" style="max-width: 100%; max-height: 200px; display: none;">
                    </div>
                `
            }
            <input type="hidden" name="content_type[]" value="${type}">
            <input type="hidden" name="content_order[]" value="${sectionCounter}">
        `;
        contentSections.appendChild(section);
        sectionCounter++;
    }

    addTextBtn.addEventListener('click', function() {
        createContentSection('text');
    });

    addImageBtn.addEventListener('click', function() {
        createContentSection('image');
    });

    contentSections.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-btn')) {
            e.target.closest('.content-section').remove();
        }
    });

    function previewImage(input) {
        const imgPreview = input.nextElementSibling.querySelector('.img-preview');
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imgPreview.src = e.target.result;
                imgPreview.style.display = 'block';
            };
            reader.readAsDataURL(input.files[0]);
        } else {
            imgPreview.src = '#';
            imgPreview.style.display = 'none';
        }
    }

    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('image-input')) {
            previewImage(e.target);
        }
    });
});