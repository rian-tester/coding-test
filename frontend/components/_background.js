import { loadFull } from "tsparticles";
import { Particles } from "react-tsparticles";

export default function Background() {
  const particlesInit = async (main) => {
    console.log("Initializing tsparticles...");
    await loadFull(main); // Load tsparticles features
  };

  return (
    <Particles
      id="tsparticles"
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
            onHover: { enable: true, mode: "repulse" },
            onClick: { enable: true, mode: "push" },
          },
          modes: {
            repulse: { distance: 100 },
            push: { quantity: 4 },
          },
        },
        background: {
          color: "#000000", // Background color
        },
      }}
    />
  );
}