const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.addEventListener('loadeddata', () => {
            setInterval(captureFrame, 300); // Capture every 300ms
        });
    });

function captureFrame() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frame = canvas.toDataURL('image/jpeg');
    fetch('/process_frame', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame: frame, user_id: 'user123' })
    })
    .then(res => res.json())
    .then(data => {
        const img = new Image();
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        };
        img.src = data.image;

        document.getElementById('angle').textContent = data.angle;
        document.getElementById('phase').textContent = data.phase;
        document.getElementById('reps').textContent = data.reps;
    });
}
