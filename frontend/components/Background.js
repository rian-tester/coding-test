import { loadFull } from "tsparticles";
import { Particles } from "react-tsparticles";
import styles from "./styles/Background.module.css";

export default function Background() {
  const particlesInit = async (main) => {
    console.log("Initializing tsparticles...");
    await loadFull(main); // Load tsparticles features
  };

  return (
    <Particles
      id={styles.tsparticles}
      init={particlesInit}
      options={{
        fullScreen: { enable: true }, // Fullscreen background
        particles: {
          number: { value: 100 },
          color: { value: "#ffffff" },
          shape: { type: "circle" },
          opacity: { value: 0.5 },
          size: { value: 3 },
          move: { enable: true, speed: 2 },
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: "repulse" }, // Only react to mouse hover
            onClick: { enable: true, mode: "push" }, // React to mouse clicks
            resize: true, // Ensure particles adjust on window resize
          },
          modes: {
            repulse: { distance: 100 }, // Repulse particles on hover
            push: { quantity: 4 }, // Add particles on click
          },
        },
        background: {
          color: "#000000", // Background color
        },
      }}
    />
  );
}