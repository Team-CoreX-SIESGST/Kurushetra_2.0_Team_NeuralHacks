// utils/fileProcessors.js
// This file contains server-side file processing logic
// For client-side usage, import from utils/fileProcessors-browser.js instead

// These imports should only be used on the server side
let mammoth = null;
let Pptx2json = null;

// Dynamically import server-side modules only when needed
const loadServerModules = async () => {
  if (typeof window === 'undefined') {
    // Server-side only
    try {
      const mammothModule = await import('mammoth');
      mammoth = mammothModule.default || mammothModule;
      
      const pptxModule = await import('pptx2json');
      Pptx2json = pptxModule.default || pptxModule;
    } catch (error) {
      console.warn('Server-side file processing modules not available:', error);
    }
  }
};

export const processFile = async (file) => {
  // This should only be called on the server side
  if (typeof window !== 'undefined') {
    throw new Error('This function should only be used on the server side. Use processFileSimple from chat components instead.');
  }

  await loadServerModules();
  
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const content = e.target.result;
        let extractedData;

        switch (file.type) {
          case "text/plain":
            extractedData = await processTextFile(content);
            break;
          case "application/pdf":
            extractedData = await processPdfFile(content);
            break;
          case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extractedData = await processDocxFile(content);
            break;
          case "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            extractedData = await processPptxFile(content, file);
            break;
          case "image/jpeg":
          case "image/png":
          case "image/gif":
            extractedData = await processImageFile(content, file);
            break;
          default:
            throw new Error("Unsupported file type");
        }

        resolve({
          name: file.name,
          type: file.type,
          size: file.size,
          data: extractedData,
        });
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = (error) => reject(error);
    reader.readAsArrayBuffer(file);
  });
};

const processTextFile = async (content) => {
  const decoder = new TextDecoder();
  return {
    text: decoder.decode(content),
  };
};

const processPdfFile = async (content) => {
  // You'll need a PDF library like pdfjs-dist
  const pdfjs = await import("pdfjs-dist/webpack");
  const pdf = await pdfjs.getDocument(content).promise;
  let text = "";

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    text += content.items.map((item) => item.str).join(" ") + "\n";
  }

  return { text };
};

const processDocxFile = async (content) => {
  const result = await mammoth.extractRawText({ arrayBuffer: content });
  return {
    text: result.value,
  };
};

const processPptxFile = async (content, file) => {
  const pptx2json = new Pptx2json();
  const result = await pptx2json.toJson(file);
  return {
    slides: result.slides,
  };
};

const processImageFile = async (content, file) => {
  // Convert image to base64 for transmission
  const base64 = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.readAsDataURL(file);
  });

  return {
    base64,
    dimensions: await getImageDimensions(content),
  };
};

const getImageDimensions = (arrayBuffer) => {
  return new Promise((resolve) => {
    const blob = new Blob([arrayBuffer]);
    const img = new Image();
    img.onload = () => {
      resolve({ width: img.width, height: img.height });
    };
    img.src = URL.createObjectURL(blob);
  });
};
