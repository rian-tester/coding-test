import React, { useState } from "react";
import styles from "./styles/RepCard.module.css";

export default function RepCard({ rep }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const totalDeals = rep.deals.length;
  const closedWonDeals = rep.deals.filter(deal => deal.status === "Closed Won").length;
  const totalValue = rep.deals.reduce((sum, deal) => sum + deal.value, 0);

  return (
    <div className={styles.card} onClick={toggleExpanded}>
      <div className={styles.cardHeader}>
        <div className={styles.profileSection}>
          <div className={styles.profileImage}>
            <img
              src={`http://localhost:8000/images/${rep.name}.webp`}
              alt={rep.name}
              className={styles.avatar}
            />
          </div>
          <div className={styles.profileInfo}>
            <h3 className={styles.name}>{rep.name}</h3>
            <p className={styles.role}>{rep.role}</p>
          </div>
        </div>
      </div>

      <div className={styles.statsSection}>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>📋</span>
          <span className={styles.statNumber}>{totalDeals}</span>
          <span className={styles.statLabel}>Total Deals</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>🏆</span>
          <span className={styles.statNumber}>{closedWonDeals}</span>
          <span className={styles.statLabel}>Won</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>💰</span>
          <span className={styles.statNumber}>${(totalValue / 1000).toFixed(0)}K</span>
          <span className={styles.statLabel}>Revenue</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>👥</span>
          <span className={styles.statNumber}>{rep.clients.length}</span>
          <span className={styles.statLabel}>Clients</span>
        </div>
      </div>

      <div className={styles.skillsSection}>
        <h4 className={styles.sectionTitle}>Skills</h4>
        <div className={styles.skillsList}>
          {rep.skills.map((skill, index) => (
            <span key={index} className={styles.skillTag}>
              {skill}
            </span>
          ))}
        </div>
      </div>

      {isExpanded && (
        <div className={styles.expandedContent}>
          <div className={styles.dealsSection}>
            <h4 className={styles.sectionTitle}>Deals</h4>
            <div className={styles.dealsList}>
              {rep.deals.map((deal, index) => (
                <div
                  key={index}
                  className={`${styles.dealItem} ${
                    deal.status === "Closed Won"
                      ? styles.dealWon
                      : deal.status === "In Progress"
                      ? styles.dealProgress
                      : styles.dealLost
                  }`}
                >
                  <div className={styles.dealInfo}>
                    <span className={styles.dealClient}>{deal.client}</span>
                    <span className={styles.dealValue}>${deal.value.toLocaleString()}</span>
                  </div>
                  <span className={styles.dealStatus}>{deal.status}</span>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.clientsSection}>
            <h4 className={styles.sectionTitle}>Clients</h4>
            <div className={styles.clientsList}>
              {rep.clients.map((client) => (
                <div key={client.id} className={styles.clientItem}>
                  <div className={styles.clientInfo}>
                    <span className={styles.clientName}>{client.name}</span>
                    <span className={styles.clientIndustry}>({client.industry})</span>
                  </div>
                  <div className={styles.clientContact}>
                    <span className={styles.clientEmail}>{client.contact.email}</span>
                    <span className={styles.clientPhone}>{client.contact.phone}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className={styles.expandIcon}>
        <span className={isExpanded ? styles.iconUp : styles.iconDown}>
          {isExpanded ? "▲" : "▼"}
        </span>
      </div>
    </div>
  );
}
