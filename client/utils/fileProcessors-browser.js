// utils/fileProcessors-browser.js
// Browser-compatible version that doesn't rely on Node.js modules

export const processFile = (file) => {
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
            extractedData = await processPptxFile(content);
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
  try {
    // Dynamic import for PDF.js
    const pdfjs = await import("pdfjs-dist/webpack");
    const pdf = await pdfjs.getDocument(content).promise;
    let text = "";

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      text += content.items.map((item) => item.str).join(" ") + "\n";
    }

    return { text };
  } catch (error) {
    console.error("Error processing PDF:", error);
    return { text: "PDF file uploaded (processing on server)" };
  }
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

const processDocxFile = async (arrayBuffer) => {
  try {
    const mammoth = await import("mammoth");
    const result = await mammoth.extractRawText({ arrayBuffer });
    return {
      text: result.value,
    };
  } catch (error) {
    console.error("Error processing DOCX:", error);
    return { text: "Error processing DOCX file" };
  }
};

const processPptxFile = async (arrayBuffer) => {
  try {
    const pptx2json = await import("pptx2json");
    const result = await pptx2json.parse(arrayBuffer);

    // Extract text from slides
    const slides = result.slides.map((slide) =>
      slide.text ? slide.text.join(" ") : "No text content"
    );

    return {
      slides,
    };
  } catch (error) {
    console.error("Error processing PPTX:", error);
    return { slides: ["Error processing PPTX file"] };
  }
};
