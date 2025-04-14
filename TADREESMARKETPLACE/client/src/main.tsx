import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Add link to Google Fonts
const linkElem = document.createElement("link");
linkElem.rel = "stylesheet";
linkElem.href = "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap";
document.head.appendChild(linkElem);

// Add link to Material Icons
const materialIconsLink = document.createElement("link");
materialIconsLink.rel = "stylesheet";
materialIconsLink.href = "https://fonts.googleapis.com/icon?family=Material+Icons";
document.head.appendChild(materialIconsLink);

// Add title
const titleElem = document.createElement("title");
titleElem.textContent = "Tadrees.com - Peer-to-Peer Tutoring Platform";
document.head.appendChild(titleElem);

// Mount app
createRoot(document.getElementById("root")!).render(<App />);
