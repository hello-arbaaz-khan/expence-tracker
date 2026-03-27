// main.js — students will add JavaScript here as features are built

// YouTube background video player
(function() {
    let player;

    // Load YouTube IFrame API
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    function onYouTubeIframeAPIReady() {
        player = new YT.Player('youtube-player', {
            height: '100%',
            width: '100%',
            videoId: '-Lt-ntUDj-g', // YouTube video ID
            playerVars: {
                'autoplay': 0,
                'controls': 1,
                'loop': 1,
                'playlist': '-Lt-ntUDj-g'
            },
            events: {
                'onReady': onPlayerReady
            }
        });
    }

    function onPlayerReady() {
        // Player is ready
    }

    // Handle video modal
    document.addEventListener('DOMContentLoaded', function() {
        const howItWorksBtn = document.getElementById('how-it-works-btn');
        const videoModal = document.getElementById('video-modal');
        const videoModalClose = document.getElementById('video-modal-close');
        const videoModalOverlay = document.querySelector('.video-modal-overlay');

        // Open modal and play video
        if (howItWorksBtn) {
            howItWorksBtn.addEventListener('click', function() {
                videoModal.classList.add('active');
                if (player && player.playVideo) {
                    player.playVideo();
                }
            });
        }

        // Close modal
        function closeModal() {
            videoModal.classList.remove('active');
            if (player && player.pauseVideo) {
                player.pauseVideo();
            }
        }

        if (videoModalClose) {
            videoModalClose.addEventListener('click', closeModal);
        }

        if (videoModalOverlay) {
            videoModalOverlay.addEventListener('click', closeModal);
        }

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && videoModal.classList.contains('active')) {
                closeModal();
            }
        });
    });

    // Expose for global access
    window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;
})();
