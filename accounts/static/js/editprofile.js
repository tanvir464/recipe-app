document.addEventListener('DOMContentLoaded', function() {
    const updatePicButton = document.getElementById('updatePicButton');
    const profilePicInput = document.getElementById('profilePic');
    const profilePicPreview = document.getElementById('profilePicPreview');

    updatePicButton.addEventListener('click', function() {
        profilePicInput.click();
    });

    profilePicInput.addEventListener('change', function() {
        if (profilePicInput.files && profilePicInput.files[0]) {
            const reader = new FileReader();

            reader.onload = function(e) {
                profilePicPreview.src = e.target.result;
            };

            reader.readAsDataURL(profilePicInput.files[0]);
        }
    });
});
