import React from "react";
import styles from "./styles/RepCard.module.css";

export default function RepCard({ rep }) {
  return (
    <li className={styles["rep-card"]}>
      <div className={styles["rep-header"]}>
        <strong>{rep.name}</strong> - {rep.role}
      </div>
      <hr className={styles["divider"]} />
      <div className={styles["rep-content"]}>
        <div className={styles["rep-image"]}>
          <img
            src={`http://localhost:8000/images/${rep.name}.webp`}
            alt={rep.name}
            className={styles["sales-image"]}
          />
        </div>
        <div className={styles["rep-details"]}>
          <ul>
            <li>
              Skills:
              <ul>
                {rep.skills.map((skill, index) => (
                  <li key={index}>{skill}</li> 
                ))}
              </ul>
            </li>
            <li>
              Deals:
              <ul>
                {rep.deals.map((deal, index) => (
                  <li
                    key={index}
                    className={`${styles["deal-item"]} ${
                      deal.status === "Closed Won"
                        ? styles["closed-won"]
                        : deal.status === "In Progress"
                        ? styles["pending"] // Correctly assign the orange color for "In Progress"
                        : styles["closed-lost"]
                    }`}
                  >
                    {deal.client} - ${deal.value} ({deal.status})
                  </li>
                ))}
              </ul>
            </li>
            <li>
              Clients:
              <ul>
                {rep.clients.map((client) => (
                  <li key={client.id}>
                    <strong>{client.name}</strong> ({client.industry})
                    <br />
                    Email: {client.contact.email}, Phone: {client.contact.phone}
                  </li>
                ))}
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </li>
  );
}