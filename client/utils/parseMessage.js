// utils/parseMessage.js
export function parseMessage(message) {
  try {
    const data = JSON.parse(message);

    // Case 1: It's a research report
    if (data && data.summary && Array.isArray(data.keyPoints)) {
      return { type: "report", data };
    }

    // Case 2: It's valid JSON but not a report → return as string
    return { type: "string", data: JSON.stringify(data, null, 2) };
  } catch (e) {
    // Case 3: Not JSON → raw text
    return { type: "string", data: message };
  }
}
