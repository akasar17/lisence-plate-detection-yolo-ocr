const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const detectBtn = document.getElementById('detectBtn');
const resultDiv = document.getElementById('result');
const validityDiv = document.getElementById('validity');
const loadingDiv = document.getElementById('loading');

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (!file) return;
  imagePreview.src = URL.createObjectURL(file);
  imagePreview.style.display = 'block';
  detectBtn.disabled = false;
  resultDiv.textContent = '';
  validityDiv.textContent = '';
});

detectBtn.addEventListener('click', async () => {
  const file = fileInput.files[0];
  if (!file) return alert('Please select an image first.');

  detectBtn.disabled = true;
  loadingDiv.style.display = 'block';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/detect', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    loadingDiv.style.display = 'none';
    detectBtn.disabled = false;

    if (!data.success || !data.detections.length) {
      resultDiv.textContent = 'No plates detected.';
      validityDiv.textContent = '';
      return;
    }

    const plate = data.detections[0].plate;
    const valid = data.detections[0].validity;
    const confidence = data.detections[0].confidence;

    resultDiv.textContent = `Detected: ${plate} (${confidence}%)`;
    validityDiv.textContent = `Status: ${valid}`;
    validityDiv.style.color = valid === 'Valid' ? 'green' : 'red';
  } catch (err) {
    console.error('Error:', err);
    loadingDiv.style.display = 'none';
    detectBtn.disabled = false;
    resultDiv.textContent = 'Something went wrong.';
  }
});
