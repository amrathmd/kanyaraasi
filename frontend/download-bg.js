const https = require('https');
const fs = require('fs');
const path = require('path');

// Create images directory if it doesn't exist
const imagesDir = path.join(__dirname, 'public', 'images');
if (!fs.existsSync(imagesDir)) {
  fs.mkdirSync(imagesDir, { recursive: true });
}

// URL of a document-themed image from Unsplash
const imageUrl = 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2070&auto=format&fit=crop';

// Download the image
https.get(imageUrl, (response) => {
  const filePath = path.join(imagesDir, 'auth-bg.jpg');
  const fileStream = fs.createWriteStream(filePath);
  
  response.pipe(fileStream);
  
  fileStream.on('finish', () => {
    fileStream.close();
    console.log('Background image downloaded successfully!');
  });
}).on('error', (err) => {
  console.error('Error downloading the image:', err.message);
}); 