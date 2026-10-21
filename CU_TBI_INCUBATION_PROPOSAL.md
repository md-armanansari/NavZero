# CU-TBI INCUBATION PROPOSAL & PRE-SEED GRANT APPLICATION
## Project: Autonomous GPS-Denied Vision-Based UAV Localization System (NavZero / Project Trishul)

**Applicant:** Student Innovator, Chandigarh University  
**Target Program:** CU-TBI Pre-Incubation / NIDHI-PRAYAS Prototype Grant (Up to ₹10 Lakhs) / NIDHI-EIR Fellowship  
**Technology Domain:** Aerospace & Defense / Autonomous Unmanned Systems / Computer Vision  
**Current Readiness:** Technology Readiness Level (TRL) 3/4 (Analytical Laboratory Prototype Complete)  
**Date:** October 2026  

---

## 1. Executive Summary

Electronic Warfare (EW) and localized Global Navigation Satellite System (GNSS) jamming have emerged as the primary failure point for tactical Unmanned Aerial Vehicles (UAVs) in modern contested border sectors (e.g., Eastern Ladakh). Commercial-off-the-shelf and standard military UAVs relying on satellite positioning experience catastrophic navigational loss, drifting, or mission abortion when GPS signals are suppressed.

**Project Trishul / NavZero** is an indigenous, edge-compute visual localization software engine that enables tactical UAVs to autonomously determine their global geodetic coordinates $(X, Y)$ and execute autonomous Return-to-Home (V-RTH) maneuvers with **zero dependence on GPS, magnetometer compasses, or external radio-frequency emissions**.

The core software pipeline is already fully developed, benchmarked, and validated on standard consumer computing budgets:
* **Real-time execution:** 26–45 frames per second on low-power quad-core CPU architecture (AMD/ARM) without requiring bulky, power-hungry dedicated GPUs.
* **Algorithmic architecture:** Multi-scale ORB (Oriented FAST and Rotated BRIEF) binary descriptors, bitwise Hamming matching, Lowe's distance ratio filtering ($d_1 < 0.75 \times d_2$), and robust projective RANSAC geometric outlier rejection.
* **Geospatial integration:** Standard 6-parameter GDAL/USGS affine coordinate transformations mapping camera frame pixels to metric map coordinates.
* **Software rigor:** 34 passing automated unit tests (100% pass rate) with sub-250MB RAM footprint.

We are seeking **formal pre-incubation, laboratory workspace access, and prototype grant funding (NIDHI-PRAYAS / TBI Seed Support)** through CU-TBI to transition this proven software engine onto an embedded physical airframe (Raspberry Pi 5 + Pixhawk 6C) for outdoor flight validation.

---

## 2. Problem Statement & National Defense Relevance

### The Operational Challenge
In contested environments, adversary ground vehicles deploy high-power Electronic Warfare (EW) jammers broadcasting broadband noise across L1/L2 satellite bands. Because satellite signals originate 20,000 km in space, their ground received power is exceptionally weak ($\approx -160\text{ dBW}$). A low-cost 50-watt ground jammer effectively denies GPS across a 20–30 km radius.

When GPS fails:
1. Conventional tactical drones enter fail-safe descent inside hostile territory or drift uncontrolled due to high-altitude crosswinds.
2. Inertial Measurement Units (IMUs) accumulate quadratic drift over time ($\sim \frac{1}{2}\epsilon_a t^2$), deviating by hundreds of meters in minutes.
3. Radio communications for manual piloting can be direction-found and jammed by enemy electronic surveillance.

### National Defense Priority
The Indian Ministry of Defence (MoD) and Innovations for Defence Excellence (iDEX) have identified **GPS-Denied UAV Navigation** as a high-priority challenge under recent Defence India Startup Challenges (DISC). Our project directly addresses this critical capability gap under the *Aatmanirbhar Bharat* and *Make in India* defense initiatives.

---

## 3. The Proposed Solution: NavZero Optical Architecture

Our system provides a passive, non-emissive "optical autopilot" that navigates by matching the physical terrain passing beneath the drone's belly camera against pre-loaded reconnaissance orthophoto tiles stored in onboard memory:

```
┌─────────────────────────┐      ┌───────────────────────────────┐
│   Downward CMOS Camera  │      │ Pre-Loaded Georeferenced Map  │
│    (Live 30 FPS Feed)   │      │   (Satellite / Aerial Ortho)  │
└────────────┬────────────┘      └──────────────┬────────────────┘
             │                                  │
             ▼                                  ▼
      [ ORB Feature ]                    [ ORB Feature ]
      [  Extraction ]                    [  Extraction ]
             │                                  │
             └─────────────────┬────────────────┘
                               │
                               ▼
               [ Bitwise Hamming Matching & ]
               [   Lowe's 0.75 Ratio Test   ]
                               │
                               ▼
               [ Projective RANSAC Filter  ]
               [ (Rejects sensor noise/fog)]
                               │
                               ▼
               [ 6-Parameter GDAL Affine   ]
               [ Coordinate Transformation ]
                               │
                               ▼
               [ Lat/Lon Coordinate Stream ]
               [     (30 Hz Update Rate)   ]
                               │
                               ▼
             ┌────────────────────────────────────┐
             │ MAVLink VISION_POSITION_ESTIMATE   │
             │   (UART Serial to Drone Pixhawk)   │
             └────────────────────────────────────┘
```

### Operational Modes:
1. **Absolute Map Matching Mode:** When satellite/aerial imagery is pre-loaded before takeoff, the drone computes exact geodetic coordinates ($\text{Lat}, \text{Lon}$) by locking onto permanent geological landmarks.
2. **Visual Odometry Breadcrumb Mode (Zero-Map):** When flying into unmapped sectors, the engine tracks inter-frame pixel displacements between consecutive frames ($t$ and $t-1$), logging an autonomous visual breadcrumb trail.
3. **Autonomous Visual Return-to-Home (V-RTH):** When primary GPS is jammed, the autopilot initiates autonomous 180° heading reversal and retraces the visual breadcrumb trail to the exact physical takeoff point without human intervention.

---

## 4. Current Technical Traction & Accomplishments (TRL 3/4)

Unlike conceptual proposals, this project is backed by a fully developed, working software implementation:

1. **Physical Real-World Validation:**
   - Operational live webcam tracking module demonstrating real-time feature correspondence at 26–45 FPS on an AMD Ryzen 5 CPU without GPU acceleration.
   - Robust lock maintained across camera pitch, roll, and tilt angles (homography perspective tracking).
2. **True Aerial Orthophoto Processing:**
   - Validated over real high-resolution photographic survey imagery with rotational offsets, achieving up to 100% geometric inlier consistency under RANSAC.
3. **Flight Simulator & Cockpit Telemetry:**
   - Interactive Software-In-The-Loop (SIL) flight simulator with real-time GPS jamming toggle and autonomous Return-to-Home triggers.
4. **Code Quality & Testing:**
   - 34 automated unit tests covering georeferencing inversions, determinant checks, Hamming matching, ratio filtering, and telemetry pipelines with 100% pass rates.
   - Comprehensive 18-section academic research report and technical documentation completed.

---

## 5. What We Are Requesting from CU-TBI

To transition this technology from **TRL 4 (Laboratory Validation)** to **TRL 6 (Physical Airframe Demonstration)**, we request:

### A. Incubation & Facilities Support
* Formal admission into CU-TBI Pre-Incubation / Incubation cohort.
* Dedicated desk/workbench space in the CU-TBI innovation workspace.
* Access to university testing facilities (outdoor sports ground / flight testing cage for safe flight tests).
* Mentorship from CU faculty in Mechatronics, Aerospace, and Embedded Systems.

### B. Lab Hardware Access (Or Prototype Grant Funding)
We do not require complex or expensive industrial machinery. We request temporary issue of existing college lab components or a seed prototype grant under **NIDHI-PRAYAS** (or internal TBI micro-grant) according to the following Bill of Materials (BOM):

| Item Description | Quantity | Purpose | Est. Cost (₹) |
| :--- | :---: | :--- | :---: |
| **Raspberry Pi 5 (8GB) + Active Cooler** | 2 | Onboard companion computer for running Python/OpenCV vision engine | ₹18,000 |
| **Pixhawk 6C / 4 Flight Controller Kit** | 1 | Open-source autopilot running ArduPilot for MAVLink telemetry | ₹16,000 |
| **Global Shutter Downward Camera Module** | 2 | High-speed, distortion-free optical ground tracking sensor | ₹8,000 |
| **F450 Quadcopter Airframe + Motors/ESCs** | 1 | Basic quadcopter test bench for outdoor flight integration | ₹14,000 |
| **LiPo Batteries (4S 5000mAh) + Smart Charger** | 2 | Propulsion and avionics power supply | ₹12,000 |
| **Benchtop Rig Hardware & Connectors** | - | Acrylic mounting plates, FTDI cables, telemetry radios | ₹7,000 |
| **Field Testing & Compliance Expenses** | - | Safety nets, ground markers, field logistics | ₹10,000 |
| **TOTAL ESTIMATED PROTOTYPE BUDGET:** | | | **₹85,000** |

*(Note: If CU robotics/aerospace laboratories already possess Pixhawk controllers and Raspberry Pis, the required cash grant can be reduced to under ₹25,000 for consumables).*

---

## 6. Milestone Execution Roadmap (6-Month Plan)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Month 1-2   │ ──▶ │  Month 3-4   │ ──▶ │   Month 5    │ ──▶ │   Month 6    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
Embedded Porting     Benchtop HIL         Tethered Hover       Outdoor Flight
(RPi 5 + OpenCV)     (Pixhawk MAVLink)    Outdoor Field Test   & iDEX Filing
```

* **Month 1–2: Embedded Optimization**  
  Port existing Python vision codebase to Raspberry Pi OS (Linux ARM64). Benchmark C++ bindings to achieve stable 30+ FPS at under 7 watts power consumption.
* **Month 3–4: Hardware-in-the-Loop (HIL) Integration**  
  Establish two-way UART serial communication between Raspberry Pi and Pixhawk flight controller using `pymavlink`. Verify simulated GPS failsafe handoff on benchtop rig without propellers.
* **Month 5: Tethered Field Testing**  
  Integrate hardware onto F450 quadcopter airframe. Conduct low-altitude tethered hover tests over college ground markers. Demonstrate GPS jamming injection and automatic optical position holding.
* **Month 6: Autonomous Return-to-Home Demonstration & Grant Applications**  
  Execute full outdoor autonomous mission: manual takeoff $\rightarrow$ GPS cut $\rightarrow$ autonomous optical return-to-home and landing. Film high-resolution video proof and submit formal application for **iDEX DISC (₹1.5 Cr)** and **Smart India Hackathon (SIH)** under Chandigarh University’s institutional banner.

---

## 7. Commercialization & Strategic Opportunity

1. **Defense Procurement (iDEX / Indian Armed Forces):**  
   The primary customer is the Indian defense ecosystem (Indian Army artillery units, Northern Command surveillance, BSF border patrol). By developing an export-free, indigenous software kit, we can retrofit existing military drone fleets with GPS-denied survivability at a fraction of imported system costs.
2. **Commercial Sector (Mining & Surveying):**  
   Underground mining tunnels, indoor industrial inspections, and deep mountain ravines frequently suffer from GPS signal blockage. Our vision navigation kit opens immediate commercial application for autonomous infrastructure inspection.
3. **Institutional Prestige for Chandigarh University:**  
   Submitting a validated TRL-6 defense project to national platforms (iDEX, DefTech, SIH) significantly enhances Chandigarh University’s NIRF research ranking, NAAC accreditation, and national media recognition.

---

## 8. Applicant Information & Commitment

* **Applicant:** Student Researcher & Developer  
* **Institution:** Chandigarh University, Punjab  
* **Software Repository:** Fully version-controlled, documented, and reproducible in local git repository (`vision_localization_research`).  
* **Demonstration Availability:** Immediate live physical demonstration of the computer vision engine, flight simulator, and unit tests can be delivered to the CU-TBI screening committee on 10 minutes notice.

---
**Submitted with Request for Consideration by the CU-TBI Screening Committee.**
