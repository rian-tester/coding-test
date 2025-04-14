import React from "react";
import styles from "./styles/Spinner.module.css";

export default function Spinner() {
  return (
    <div className={styles.spinner}>
      <div className={styles.doubleBounce1}></div>
      <div className={styles.doubleBounce2}></div>
    </div>
  );
}