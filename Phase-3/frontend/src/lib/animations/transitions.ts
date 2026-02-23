// Reusable transition configurations

export const defaultTransition = {
  duration: 0.3,
  ease: "easeOut",
};

export const fastTransition = {
  duration: 0.15,
  ease: "easeOut",
};

export const slowTransition = {
  duration: 0.5,
  ease: "easeInOut",
};

export const springTransition = {
  type: "spring",
  stiffness: 300,
  damping: 30,
};

export const pageTransition = {
  duration: 0.4,
  ease: [0.4, 0, 0.2, 1],
};
