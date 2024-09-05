document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const recipeId = window.location.pathname.split('/').filter(Boolean).pop();
    const cancelRatingBtn = document.getElementById('cancel-rating');

    function setupRatingListeners() {
        document.querySelectorAll('.rating .user-star').forEach(function(star) {
            star.addEventListener('click', function() {
                const value = this.getAttribute('data-value');
                rateRecipe(value);
            });
        });

        cancelRatingBtn.addEventListener('click', cancelRating);
    }

    function rateRecipe(value) {
        fetch(`/recipes/${recipeId}/rate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `rating=${value}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateUserRating(data.user_rating);
                updateAverageRating(data.avg_rating, data.rating_count);
                showCancelButton();
            } else {
                console.error('Error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function cancelRating() {
        fetch(`/recipes/recipe/${recipeId}/cancel_rate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateUserRating(0);
                updateAverageRating(data.avg_rating, data.rating_count);
                hideCancelButton();
            } else {
                console.error('Error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateUserRating(rating) {
        const stars = document.querySelectorAll('.rating .user-star');
        stars.forEach(function(star, index) {
            if (index < rating) {
                star.classList.remove('far');
                star.classList.add('fas');
            } else {
                star.classList.remove('fas');
                star.classList.add('far');
            }
        });
    }

    function updateAverageRating(avgRating, count) {
        document.getElementById('avg-rating').innerHTML = `<b>Avg: ${avgRating.toFixed(1)}/5 (${count})</b>`;
    }

    function showCancelButton() {
        cancelRatingBtn.style.display = 'inline-block';
    }

    function hideCancelButton() {
        cancelRatingBtn.style.display = 'none';
    }

    fetch(`/recipes/recipe/${recipeId}/details/`)
        .then(response => response.json())
        .then(data => {
            updateUserRating(data.user_rating);
            updateAverageRating(data.avg_rating, data.rating_count);
            if (data.user_rating > 0) {
                showCancelButton();
            }
        })
        .catch(error => console.error('Error:', error));

    setupRatingListeners();

    document.querySelectorAll('.reply-link').forEach(function(replyLink) {
        replyLink.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const container = document.getElementById(`reply-form-container-${commentId}`);

            if (container.querySelector('form')) {
                container.innerHTML = '';
                this.textContent = 'Reply';
            } else {
                const template = document.getElementById('reply-form-template');
                const clone = template.content.cloneNode(true);
                const form = clone.querySelector('form');
                form.action = `/recipes/recipe/${recipeId}/add_comment/`;
                form.querySelector('[name="parent_id"]').value = commentId;
                container.appendChild(clone);
                this.textContent = 'Hide';
            }
        });
    });

    document.querySelectorAll('.reaction').forEach(function(reaction) {
        reaction.addEventListener('click', function() {
            const contentType = this.getAttribute('data-type');
            const contentId = this.getAttribute('data-id');

            fetch('/recipes/toggle_reaction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `content_type=${contentType}&content_id=${contentId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.classList.toggle('loved');
                    this.querySelector('.reaction-count').textContent = data.reaction_count;
                } else {
                    console.error('Error:', data.error);
                }
            });
        });
    });

    document.querySelectorAll('.delete-comment').forEach(function(deleteButton) {
        deleteButton.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            fetch(`/recipes/delete_comment/${commentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commentElement = this.closest('.comment');
                    commentElement.remove();
                    const replies = document.querySelectorAll(`.reply[data-parent-id="${commentId}"]`);
                    replies.forEach(reply => reply.remove());
                } else {
                    console.error('Error:', data.error);
                }
            });
        });
    });

    document.querySelectorAll('.delete-reply').forEach(function(deleteButton) {
        deleteButton.addEventListener('click', function() {
            const replyId = this.getAttribute('data-reply-id');
            fetch(`/recipes/delete_comment/${replyId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.closest('.reply').remove();
                } else {
                    console.error('Error:', data.error);
                }
            });
        });
    });
});