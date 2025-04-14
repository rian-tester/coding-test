import { useState, useEffect } from "react";

export default function AudioPlayer({ soundEnabled, setSoundEnabled }) {
  const [audio, setAudio] = useState(null); // Store the audio instance
  const [soundLoading, setSoundLoading] = useState(true); // Track if the sound is loading

  // Initialize audio and prepare for autoplay
  useEffect(() => {
    const audioInstance = new Audio("/sounds/backsounds.mp3");
    audioInstance.loop = true; // Enable looping
    setAudio(audioInstance);

    // Wait for the audio to load
    audioInstance.addEventListener("canplaythrough", () => {
      setSoundLoading(false); // Sound is ready
    });

    // Add a listener for user interaction to unlock autoplay
    const unlockAudio = () => {
      if (soundEnabled) {
        try {
          audioInstance.play();
        } catch (error) {
          console.error("Error playing sound:", error);
        }
      }
      // Remove the event listener after the first interaction
      window.removeEventListener("click", unlockAudio);
      window.removeEventListener("keydown", unlockAudio);
    };

    window.addEventListener("click", unlockAudio);
    window.addEventListener("keydown", unlockAudio);

    return () => {
      audioInstance.pause(); // Pause audio when component unmounts
      audioInstance.removeEventListener("canplaythrough", () => {}); // Clean up event listener
      window.removeEventListener("click", unlockAudio);
      window.removeEventListener("keydown", unlockAudio);
    };
  }, [soundEnabled]);

  // Toggle sound setting
  const toggleSound = () => {
    const newState = !soundEnabled;
    setSoundEnabled(newState);
    localStorage.setItem("soundEnabled", JSON.stringify(newState));

    if (newState) {
      audio.play().catch((error) => {
        console.error("Error playing sound:", error);
      });
    } else {
      audio.pause();
    }
  };

  return (
    <>
      {/* Show Spinner While Sound is Loading */}
      {soundLoading && <div className="spinner">Loading sound...</div>}

      {/* Sound Toggle Button */}
      <button className="sound-toggle" onClick={toggleSound}>
        {soundEnabled ? "🔇" : "🔊"}
      </button>
    </>
  );
}