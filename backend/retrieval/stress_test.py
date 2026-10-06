import os
import sys
import time
import numpy as np
import pandas as pd
from backend.retrieval.search_patents import get_retrieval_resources, semantic_search

# ----------------------------------------------------------------------
# 50 REALISTIC PATENT INVENTION IDEAS ACROSS 10 TECH CATEGORIES
# ----------------------------------------------------------------------
INVENTIONS = [
    # 1. AI
    {
        "id": "AI_1", "category": "AI",
        "short": "Deep learning system for real-time classification of dermoscopic skin lesion images.",
        "medium": "An automated system utilizing convolutional neural networks to classify skin lesions in real-time. The method preprocesses dermoscopic images to normalize contrast and highlights features. It outputs classification probabilities alongside diagnostic confidence intervals.",
        "long": "A computer-implemented method for real-time diagnostic support of dermatological conditions using deep neural networks. The system receives a high-resolution dermoscopic image of a skin lesion from a mobile camera interface. An image preprocessing pipeline performs color normalization, illumination correction, and hair-removal filtering using morphological operations. The cleaned image is passed through a convolutional neural network architecture, specifically a modified residual network pre-trained on diverse dermatological datasets, which extracts multi-scale spatial features. The final layer uses a softmax activation function to compute class probabilities across melanoma, basal cell carcinoma, and benign nevus categories. Additionally, an uncertainty estimation layer utilizing Monte Carlo dropout computes diagnostic confidence intervals. The probability distribution and confidence scores are formatted into a graphical clinical report and displayed to the practitioner within 200 milliseconds."
    },
    {
        "id": "AI_2", "category": "AI",
        "short": "Transformer-based language model for automated summary generation of legal contract clauses.",
        "medium": "A system using pre-trained transformer models to generate summaries of legal contract clauses. The method segments legal documents into discrete clauses and tokenizes them. It outputs simplified, plain-language summaries highlighting obligations and liabilities.",
        "long": "An automated system for legal contract analysis and text summarization using generative transformer architectures. The system ingests unstructured legal documents in PDF or DOCX formats and executes a layout parser to identify document boundaries, headers, and individual clauses. Each clause is parsed, and irrelevant formatting is stripped. The segmented text is tokenized using a byte-pair encoding vocabulary optimized for legal terminology. The tokens are input into a bidirectional encoder-decoder transformer network fine-tuned on annotated contract summaries. The decoder generates plain-language, simplified summaries that highlight key legal concepts, including indemnification obligations, limitation of liability thresholds, and contract termination triggers. A post-processing module verifies that numerical entities like dates and monetary values are preserved accurately in the output. The resulting summaries are displayed alongside the original clauses in a comparative interface."
    },
    {
        "id": "AI_3", "category": "AI",
        "short": "Generative adversarial network for synthetic MRI scan synthesis to train medical models.",
        "medium": "A method employing generative adversarial networks to synthesize high-fidelity MRI scans. The generator synthesizes scans from noise vectors while the discriminator evaluates realism. The synthesized scans expand training datasets for medical segmentation algorithms.",
        "long": "A generative adversarial network (GAN) framework for synthesizing high-resolution, three-dimensional synthetic magnetic resonance imaging (MRI) scans for medical data augmentation. The system includes a generator network utilizing a 3D U-Net architecture with residual blocks and skip connections, and a patch-based discriminator network that classifies scans as real or synthetic. The generator receives a random latent noise vector conditioned on specific clinical attributes, such as patient age and lesion presence, and outputs synthetic MRI volumes showing realistic anatomical structures. The discriminator evaluates the structural coherence and texture maps of the generated scans. During training, a combined loss function consisting of adversarial loss, cycle-consistency loss, and structural similarity index (SSIM) loss is minimized. The resulting high-fidelity synthetic scans are stored in a database and utilized to train downstream machine learning algorithms for automated brain tumor segmentation, mitigating data scarcity and privacy issues."
    },
    {
        "id": "AI_4", "category": "AI",
        "short": "Reinforcement learning agent for dynamic traffic signal coordination in urban grids.",
        "medium": "A traffic signal control system utilizing reinforcement learning agents to minimize congestion in urban grids. The agent receives traffic density inputs from camera feeds at intersections. It adjusts signal timings dynamically to maximize traffic flow.",
        "long": "A decentralized traffic management system for urban road networks utilizing multi-agent reinforcement learning. Each intersection in an urban grid is controlled by a local agent. The agent interfaces with vehicle detection sensors, including loop detectors and video cameras, to receive real-time state inputs representing queue lengths, vehicle wait times, and traffic densities on incoming lanes. The agent's action space consists of selecting the active phase combination and duration for the traffic signals. The reward function is defined as the negative sum of vehicle delay times and queue lengths across the intersection. Agents communicate traffic flow states with adjacent intersections to coordinate green wave patterns across grid corridors. The system updates neural network weights dynamically using deep Q-learning, adapting to changing traffic volumes during peak hours and reducing average commute times across the grid."
    },
    {
        "id": "AI_5", "category": "AI",
        "short": "Anomalous user behavior detection in cloud networks using graph neural networks.",
        "medium": "A security system mapping cloud network interactions to dynamic graphs and using graph neural networks to detect anomalies. The system tracks user accesses, IP addresses, and database queries. It identifies anomalous nodes and paths indicative of data breaches.",
        "long": "A security system and method for detecting malicious insider threats and unauthorized access in cloud enterprise networks using graph neural networks (GNNs). The system monitors network activity logs, database access queries, and API calls to construct a dynamic, directed graph representation of cloud interactions. In this graph, nodes represent users, devices, service accounts, and data objects, while edges represent actions such as logins, data reads, or configuration changes. Node attributes are populated with metadata including access times, data volumes, and geolocation markers. A graph convolutional network (GCN) processes the graph structure to generate low-dimensional node embeddings that capture structural relationships. An anomaly detection classifier evaluates these embeddings against historical baselines. Transactions or user paths showing anomalous scores indicative of data exfiltration or credential hijacking trigger automated security alerts and isolate the compromised nodes."
    },

    # 2. Healthcare
    {
        "id": "HC_1", "category": "Healthcare",
        "short": "Non-invasive optical sensor system for continuous blood glucose monitoring.",
        "medium": "A wearable optical sensor system for non-invasive, continuous blood glucose monitoring. The device emits near-infrared light through the skin and measures absorption. A processor translates absorption spectra into glucose levels.",
        "long": "A wearable medical device for non-invasive, continuous monitoring of blood glucose levels using near-infrared spectroscopy. The device is housed in a wristband and includes a multi-wavelength light-emitting diode (LED) array that emits light in the range of 800 to 2500 nanometers. The emitted light is directed through the skin tissue of the user's wrist, where it interacts with interstitial fluid glucose. A photodiode detector array measures the backscattered light intensity. A digital signal processor filters out ambient noise and motion artifacts using accelerometer inputs. The processor applies a multivariate calibration model, using partial least squares regression, to convert the measured absorption spectra into real-time blood glucose concentration values. The results are transmitted via Bluetooth Low Energy to a smartphone application for display, and stored in a secure cloud server for physician review."
    },
    {
        "id": "HC_2", "category": "Healthcare",
        "short": "Smart pill bottle with integrated weight sensors for automated adherence tracking.",
        "medium": "A medication adherence tracking system featuring a smart pill bottle with weight sensors. The bottle weighs its contents continuously to verify dosage removal. It transmits compliance metadata to caregivers and medical providers.",
        "long": "An automated medication compliance system comprising a smart pill bottle and associated communication server. The pill bottle features a capacitive weight sensor array integrated into its base, which measures the combined weight of the stored medication. A micro-switch in the cap assembly detects opening and closing events. An onboard microcontroller receives inputs from the weight sensor and the cap switch to calculate the quantity of medication removed during each event. If the weight change does not match the prescribed dosage at the scheduled time, a buzzer alerts the patient. The microcontroller transmits adherence logs, including timestamps and dosage counts, over a cellular link to a remote health platform, enabling real-time monitoring of patient compliance."
    },
    {
        "id": "HC_3", "category": "Healthcare",
        "short": "Automated external defibrillator with real-time audio guidance based on chest impedance.",
        "medium": "An automated external defibrillator providing customized CPR audio guidance. The device measures thoracic impedance through electrode pads during compressions. It adjusts compression depth instructions dynamically based on feedback.",
        "long": "An automated external defibrillator (AED) system featuring dynamic, real-time audio and visual CPR feedback. The AED includes self-adhesive electrode pads containing integrated pressure sensors, which are applied to the patient's chest. During resuscitation, the device continuously measures the patient's thoracic impedance through the electrode pads to monitor ventilations and heart rhythms. Additionally, the pressure sensors measure the rate and depth of chest compressions. An internal processor analyzes the compression depth and rate, and compares them against cardiopulmonary resuscitation guidelines. The device outputs real-time audio prompts, such as 'compress harder' or 'slow down,' adjusting the instructions based on the feedback to optimize CPR quality."
    },
    {
        "id": "HC_4", "category": "Healthcare",
        "short": "Intelligent orthopedic knee brace with flex sensors to guide rehabilitation.",
        "medium": "A wearable knee brace featuring flex sensors to monitor range of motion during rehabilitation. The brace tracks joint flexion and extension during exercises. It displays progress metrics and alerts users of harmful movements via an app.",
        "long": "A smart orthopedic knee brace for monitoring and guiding physical rehabilitation. The brace consists of a neoprene sleeve containing integrated flexible resistive bend sensors aligned with the user's knee joint. A battery-powered microcontroller unit attached to the brace samples joint angles continuously during rehabilitation exercises. The microcontroller calculates flexion and extension range of motion, angular velocity, and total repetition counts. The data is transmitted to a mobile application, which displays real-time exercise feedback and guides the user through prescribed physical therapy protocols. If the brace detects joint hyperextension or load patterns exceeding safety thresholds, it triggers a vibration motor to alert the user and prevent joint reinjury."
    },
    {
        "id": "HC_5", "category": "Healthcare",
        "short": "Microfluidic lab-on-a-chip for rapid multi-pathogen detection from saliva samples.",
        "medium": "A microfluidic cartridge for rapid detection of multiple pathogens from saliva. The chip utilizes capillary channels to distribute the sample to reaction chambers. Amplified target DNA binds to fluorescent probes for detection.",
        "long": "A microfluidic lab-on-a-chip device for rapid, multiplexed detection of viral and bacterial pathogens in saliva samples. The device comprises a disposable polymer cartridge with an inlet port, capillary micro-channels, mixing chambers, and reaction zones. A saliva sample is mixed with lysis buffer and drawn through the channels by capillary action. The sample is distributed to separate reaction chambers pre-loaded with primers for target pathogens, including influenza and SARS-CoV-2. Loop-mediated isothermal amplification (LAMP) is executed within the chambers using integrated heating elements. Amplified DNA binds to target-specific fluorescent molecular probes. An optical sensor array detects fluorescence, transmitting diagnostic results to an integrated screen within 15 minutes."
    },

    # 3. Biotech
    {
        "id": "BT_1", "category": "Biotechnology",
        "short": "CRISPR-Cas9 gene editing delivery vehicle using lipid nanoparticles for liver target.",
        "medium": "A delivery vehicle for CRISPR-Cas9 components targeting liver cells using lipid nanoparticles. The nanoparticles encapsulate Cas9 mRNA and guide RNA. They bind specifically to hepatocyte receptors to enable gene correction.",
        "long": "A composition for targeted delivery of gene editing machinery to hepatic cells in vivo. The composition comprises lipid nanoparticles (LNPs) encapsulating a Cas9 messenger RNA (mRNA) sequence and a single guide RNA (sgRNA) targeted to a genetic locus associated with hypercholesterolemia. The LNPs are formulated with an ionizable cationic lipid, a helper phospholipid, cholesterol, and a PEGylated lipid. The outer shell of the LNP is conjugated with apolipoprotein E ligands that bind specifically to low-density lipoprotein (LDL) receptors on hepatocytes. Upon intravenous administration, the LNPs are internalized by hepatocytes via receptor-mediated endocytosis, releasing the gene editing components into the cytoplasm to execute target gene cleavage and therapeutic correction."
    },
    {
        "id": "BT_2", "category": "Biotechnology",
        "short": "Bioreactor with automated pH and dissolved oxygen control for monoclonal antibody yield.",
        "medium": "A cell culture bioreactor with automated feedback control of pH and dissolved oxygen. The system uses optical sensors to monitor culture conditions. It adjusts gas flow rates and nutrient feeds dynamically to optimize antibody yield.",
        "long": "A closed-loop cell culture bioreactor system for optimizing the yield of monoclonal antibodies from mammalian cell lines. The bioreactor vessel is equipped with optical pH sensors, dissolved oxygen (DO) probes, and temperature sensors. A programmable logic controller (PLC) receives continuous measurements from the sensors. To maintain optimal growth conditions, the PLC regulates gas mass flow controllers to adjust oxygen and carbon dioxide sparging. It also controls peristaltic pumps to feed acid/base buffers and concentrated glucose feeds dynamically. The system applies predictive control models to maintain pH and DO levels within narrow optimal ranges, reducing cell shear stress and maximizing cell viability and protein production."
    },
    {
        "id": "BT_3", "category": "Biotechnology",
        "short": "Enzymatic method for rapid lignin degradation in paper pulp manufacturing.",
        "medium": "An enzymatic method utilizing laccase enzymes to degrade lignin in paper pulp manufacturing. The method treats wood pulp with a laccase-mediator system. It reduces chemical bleaching requirements and environmental waste.",
        "long": "A method for the enzymatic delignification of wood pulp in paper manufacturing. The process involves treating raw wood pulp with a formulation containing recombinant laccase enzymes derived from Trametes versicolor, in combination with a synthetic mediator compound. The treatment is conducted in an aqueous slurry at a temperature of 50 degrees Celsius and a pH of 4.5. The laccase-mediator system oxidizes phenolic and non-phenolic lignin structures, breaking the ether linkages that bind lignin to cellulose fibers. This enzymatic preprocessing selectively degrades lignin while preserving cellulose integrity, reducing the subsequent requirements for chlorine-based bleaching chemicals and decreasing chemical oxygen demand (COD) in wastewater effluent."
    },
    {
        "id": "BT_4", "category": "Biotechnology",
        "short": "Biosensor based on functionalized gold nanoparticles for detecting pesticide residues.",
        "medium": "A biosensor utilizing gold nanoparticles functionalized with specific antibodies to detect pesticide residues. The nanoparticles aggregate in the presence of pesticides. This aggregation causes a visible color change indicating contamination.",
        "long": "A colorimetric biosensor for detecting organophosphate pesticide residues in agricultural runoff. The biosensor comprises colloidal gold nanoparticles functionalized with monoclonal antibodies specific to chlorpyrifos. In the absence of chlorpyrifos, the nanoparticles remain dispersed in solution, displaying a red color. When chlorpyrifos is introduced, the antibodies bind to the pesticide molecules, causing aggregation of the gold nanoparticles due to cross-linking. This aggregation shifts the localized surface plasmon resonance, causing a color change from red to blue. The color shift is measured using a spectrophotometer or a smartphone camera, enabling rapid field testing of agricultural water samples."
    },
    {
        "id": "BT_5", "category": "Biotechnology",
        "short": "Synthetic promoter construct for high-level expression of recombinant proteins in yeast.",
        "medium": "A synthetic DNA promoter construct designed to drive high-level expression of recombinant proteins in yeast. The promoter contains engineered transcription factor binding sites. It increases protein yields compared to native promoters.",
        "long": "A synthetic DNA promoter sequence for driving high-level transcription of recombinant genes in Saccharomyces cerevisiae. The promoter construct is engineered by assembling multiple consensus binding sites for key yeast transcription factors, including Gcn4 and Gal4, separated by optimized spacer sequences. The synthetic promoter is placed upstream of a multiple cloning site containing a target gene encoding human insulin. When introduced into yeast cells, the engineered binding sites recruit RNA polymerase II, driving transcription. Cell culture experiments show that the synthetic promoter construct yields a five-fold increase in target protein expression compared to native ADH1 or TEF1 promoters, optimizing yeast expression systems for industrial biomanufacturing."
    },

    # 4. Comm
    {
        "id": "CM_1", "category": "Communication",
        "short": "Dynamic beamforming method for 5G cellular base stations using user location.",
        "medium": "A beamforming method for 5G base stations that steers radio beams dynamically based on user location. The station calculates angle-of-arrival from user signals. It concentrates signal power to improve link budget and data rates.",
        "long": "A dynamic beamforming control system and method for 5G cellular base stations utilizing phased array antennas. The base station antenna array comprises multiple active transceiver elements. A digital signal processor continuously calculates the angle-of-arrival (AoA) of uplink signals transmitted by connected user equipment (UE). Based on the AoA, the processor adjusts the relative phase and amplitude of signals fed to the antenna elements, steering narrow, high-gain downlink beams toward the UE. If the UE moves, the base station tracks its location dynamically to update the beam direction. This spatial multiplexing concentrates signal power, increases signal-to-interference-plus-noise ratio (SINR), and maximizes spectral efficiency."
    },
    {
        "id": "CM_2", "category": "Communication",
        "short": "Orthogonal frequency-division multiplexing subcarrier allocation method for cognitive radio.",
        "medium": "An OFDM subcarrier allocation method designed to prevent interference in cognitive radio systems. The system senses licensed spectrum bands to locate unused channels. It allocates subcarriers to secondary users dynamically.",
        "long": "A method for dynamic subcarrier allocation in orthogonal frequency-division multiplexing (OFDM) based cognitive radio networks. The secondary user transceiver scans licensed spectrum bands to construct a spectral occupancy map. The transceiver identifies unused subcarrier channels and allocates them for secondary transmission. To prevent interference with primary users, the system calculates the spectral distance and sidelobe leakage of adjacent active channels. It adjusts the power spectral density of secondary subcarriers dynamically, inserting spectral nulls where necessary. This dynamic allocation maximizes data throughput for secondary users while maintaining primary user link quality."
    },
    {
        "id": "CM_3", "category": "Communication",
        "short": "Low-density parity-check code decoder architecture for high-speed fiber-optic links.",
        "medium": "A low-density parity-check (LDPC) decoder architecture optimized for high-speed fiber-optic links. The hardware executes belief propagation decoding algorithms in parallel. It reduces latency and error rates in data transmission.",
        "long": "A hardware decoder architecture for decoding low-density parity-check (LDPC) forward error correction codes in high-speed optical fiber links. The decoder is implemented on an application-specific integrated circuit (ASIC) and features a parallel array of variable node units (VNUs) and check node units (CNUs) connected through a routing network. The decoder receives soft-decision information from an optical receiver and executes a sum-product belief propagation algorithm. The parallel processing structure allows concurrent updates of node values, reducing decoding latency. A dynamic quantization module scales check values during iterations, preventing arithmetic overflow and reducing bit error rates at transmission speeds exceeding 400 Gigabits per second."
    },
    {
        "id": "CM_4", "category": "Communication",
        "short": "Wireless ad-hoc network routing protocol using node battery and link stability.",
        "medium": "A routing protocol for wireless ad-hoc networks that selects paths based on battery levels and link stability. Nodes share battery status and link quality metrics. The system routing protocol avoids low-power nodes to extend network lifetime.",
        "long": "A routing protocol for mobile ad-hoc networks (MANETs) designed to maximize network lifetime and link stability. Each mobile node in the network monitors its residual battery capacity and computes a link stability index based on received signal strength indicator (RSSI) history. When a source node initiates route discovery, it broadcasts a route request packet. Intermediate nodes append their battery status and link stability indices to the packet. The destination node evaluates candidate paths using a joint metric that prioritizes routes with high remaining energy and stable connections, avoiding low-power nodes. This protocol distributes routing overhead, prevents link failures, and increases network reliability."
    },
    {
        "id": "CM_5", "category": "Communication",
        "short": "Secure multi-user MIMO broadcast method using artificial noise injection.",
        "medium": "A security method for multi-user MIMO networks using artificial noise injection. The transmitter projects signals to authorized users while injecting noise into the null spaces. The noise degrades eavesdropper decoding capabilities.",
        "long": "A secure transmission method for multi-user multiple-input multiple-output (MIMO) wireless networks. The base station is equipped with multiple antennas and transmits independent data streams to authorized users. The base station calculates the channel state information (CSI) for all authorized users. It projects the information signals directly into the channel spaces of the users, while generating and injecting artificial noise into the null space of the users' channels. The noise is designed to align with potential eavesdropper channels, degrading their signal-to-noise ratio. This security method prevents unauthorized interception of transmitted data streams without affecting the data rates of authorized users."
    },

    # 5. CS
    {
        "id": "CS_1", "category": "Computer Science",
        "short": "Distributed key-value database system with adaptive replication based on query hotness.",
        "medium": "A distributed key-value database system that replicates data dynamically based on query frequency. The system monitors access counts for data keys. It creates additional replicas of 'hot' keys to distribute read loads.",
        "long": "A distributed key-value database system and method for dynamic data replication. The database is hosted across a cluster of server nodes. A monitoring module tracks query access counts for each key, calculating a 'hotness' metric. When the access frequency of a key exceeds a replication threshold, the system replicates the key-value pair to additional nodes in the cluster. Read queries are distributed among the replicas using a load-balancing algorithm, reducing read latencies. If the access frequency of a key decreases below a threshold, the system deletes redundant replicas to conserve storage space. This adaptive replication optimizes cluster resource usage and maintains low latency during traffic spikes."
    },
    {
        "id": "CS_2", "category": "Computer Science",
        "short": "Compiler optimization method for register allocation using graph coloring heuristics.",
        "medium": "A compiler optimization method that improves register allocation using graph coloring heuristics. The compiler constructs an interference graph of variable lifetimes. It colors the graph to allocate variables to hardware registers.",
        "long": "A compiler optimization method for allocating variables to a finite set of hardware registers. The compiler analyzes intermediate code to construct a variable interference graph, where nodes represent variables and edges connect variables that are simultaneously live. The compiler applies a graph coloring heuristic to color the graph, where each color corresponds to a physical register. If the graph cannot be colored using the available registers, the compiler selects variables to spill to memory based on loop nesting depth and access frequencies. This register allocation reduces memory access operations and optimizes execution speeds of compiled machine code."
    },
    {
        "id": "CS_3", "category": "Computer Science",
        "short": "Virtual machine hypervisor memory ballooning control method to prevent swapping.",
        "medium": "A memory ballooning control method for virtual machine hypervisors to optimize memory usage. The hypervisor monitors memory utilization across virtual machines. It adjusts balloon driver allocations dynamically to prevent disk swapping.",
        "long": "A method for dynamic memory management in virtualized server environments. A hypervisor monitors memory utilization metrics, including page fault rates and free memory space, across virtual machines (VMs). If a VM experiences high memory pressure, the hypervisor activates a balloon driver in an idle VM. The balloon driver allocates and pins memory pages, returning them to the hypervisor. The hypervisor then assigns the freed memory pages to the high-pressure VM. This memory redistribution prevents VMs from swapping memory to disk, maintaining performance across the virtualized environment."
    },
    {
        "id": "CS_4", "category": "Computer Science",
        "short": "Automated software testing method using genetic algorithms to generate test inputs.",
        "medium": "A software testing method that generates test inputs using genetic algorithms. The system mutates inputs and evaluates code coverage. It evolves input populations to maximize path execution and locate software bugs.",
        "long": "An automated system and method for software test data generation. The system parses source code to identify control flow paths and targets. It applies a genetic algorithm to evolve a population of test inputs. The fitness function is defined as the code coverage achieved by executing the software with the inputs, measured by branch and path coverage. During generations, inputs that execute new code branches are selected for mutation and crossover. The system generates diverse test inputs that maximize code coverage, locating edge-case inputs and software bugs without manual script writing."
    },
    {
        "id": "CS_5", "category": "Computer Science",
        "short": "Data compression method using adaptive Huffman coding on streaming sensor data.",
        "medium": "A compression method for streaming sensor data using adaptive Huffman coding. The encoder monitors symbol frequencies in the data stream. It updates the Huffman tree dynamically to maintain compression ratios.",
        "long": "A method for compressing streaming sensor data in internet of things (IoT) devices. The IoT device receives continuous sensor readings, such as temperature or vibration values. The encoder tokenizes the data into symbols and monitors symbol frequencies within a sliding time window. It updates an adaptive Huffman tree dynamically, assigning shorter codes to frequent symbols. The compressed bitstream is transmitted over a wireless link. By adapting the coding scheme to changes in the data stream, the method maintains compression ratios, reducing transmission bandwidth and energy consumption."
    },

    # 6. Electronics
    {
        "id": "EL_1", "category": "Electronics",
        "short": "Low-power analog-to-digital converter architecture using successive approximation.",
        "medium": "A low-power SAR analog-to-digital converter architecture. The design features a charge-redistribution DAC with split capacitor arrays. It minimizes switching energy and clock distribution power.",
        "long": "A low-power successive approximation register (SAR) analog-to-digital converter (ADC) circuit. The ADC comprises a sample-and-hold circuit, a comparator, a SAR control logic block, and a charge-redistribution digital-to-analog converter (DAC). The DAC features a split capacitor array divided into main and sub-capacitors by a coupling capacitor. During conversion, the control logic executes a switching scheme that minimizes charge transfer between capacitors. Additionally, a dynamic comparator shuts down bias currents between clock phases. This architecture reduces switching energy, clock distribution power, and total energy consumption, making the ADC suitable for battery-powered sensor nodes."
    },
    {
        "id": "EL_2", "category": "Electronics",
        "short": "Phase-locked loop synthesizer circuit with digital loop filter for low jitter.",
        "medium": "A phase-locked loop (PLL) synthesizer circuit designed for low jitter. The PLL features a digital loop filter and a digitally controlled oscillator. It reduces phase noise and clock synchronization times.",
        "long": "A phase-locked loop (PLL) frequency synthesizer circuit featuring a digital loop filter. The PLL comprises a phase detector, a time-to-digital converter (TDC), a digital loop filter, a digitally controlled oscillator (DCO), and a feedback frequency divider. The TDC measures phase differences between reference and feedback clocks, outputting digital error codes. The digital loop filter processes the error codes using proportional-integral control algorithms, generating control words for the DCO. The DCO adjusts its output frequency based on the control words. The digital loop filter reduces analog component leakage, phase noise, and clock jitter."
    },
    {
        "id": "EL_3", "category": "Electronics",
        "short": "Thermal management system for integrated circuits using embedded microchannels.",
        "medium": "A thermal management system for integrated circuits utilizing embedded microchannels. The silicon substrate features microchannels for coolant circulation. An external pump regulates flow rates based on temperature sensor inputs.",
        "long": "A thermal management system for high-power integrated circuits. The silicon substrate of the integrated circuit features etched microchannels aligned with hot spots. The system includes a closed-loop coolant circulation system connected to the microchannels, an electromagnetic pump, and a heat exchanger. Temperature sensors embedded in the silicon substrate monitor temperature profiles. A microcontroller receives sensor inputs and regulates the pump to adjust coolant flow rates. The microchannel cooling removes heat directly from the silicon, preventing thermal degradation and maintaining device reliability."
    },
    {
        "id": "EL_4", "category": "Electronics",
        "short": "High-efficiency class-D audio amplifier circuit with feedback error correction.",
        "medium": "A class-D audio amplifier circuit designed for high efficiency and low distortion. The design includes a pulse-width modulator and a feedback error loop. It corrects output stage anomalies to maintain audio quality.",
        "long": "A high-efficiency class-D audio amplifier circuit. The amplifier comprises an input stage, a pulse-width modulator (PWM), a gate driver, a half-bridge output stage, and an LC low-pass filter. The circuit features an analog feedback loop connected from the switching output to the input stage. The feedback loop includes an integrator that calculates error differences between the input signal and the output voltage. The error is injected into the PWM stage, correcting distortion caused by power supply variations and output switch anomalies. This feedback loop improves total harmonic distortion (THD) while maintaining class-D efficiency."
    },
    {
        "id": "EL_5", "category": "Electronics",
        "short": "Wearable energy harvesting circuit using thermoelectric generators and boost converter.",
        "medium": "An energy harvesting circuit that converts body heat to electricity using thermoelectric generators. The circuit features an ultra-low-voltage boost converter. It accumulates energy in a supercapacitor to power wearable sensors.",
        "long": "An energy harvesting circuit for wearable electronic devices. The circuit interfaces with a thermoelectric generator (TEG) positioned on a user's skin, which generates a low voltage from body heat. The circuit features an ultra-low-voltage boost converter that steps up the TEG output from 20 millivolts to 3.3 volts. The boost converter includes a startup oscillator that operates at low input voltages. A maximum power point tracking (MPPT) module optimizes impedance matching with the TEG. The stepped-up voltage is used to charge a supercapacitor, providing power to wearable biosensors and wireless transmitters."
    },

    # 7. ME
    {
        "id": "ME_1", "category": "Mechanical Engineering",
        "short": "Planetary gear transmission system with load sharing pin configuration.",
        "medium": "A planetary gear transmission system with improved load sharing. The planet gears are mounted on flexible pins. The pins flex under load to distribute forces evenly among the gears.",
        "long": "A planetary gear transmission system designed for high load capacity and even wear. The transmission comprises a sun gear, a ring gear, a planet carrier, and multiple planet gears. Each planet gear is mounted on the planet carrier using a flexible pin assembly. The flexible pin includes an inner sleeve and an outer spindle separated by an elastomer layer. Under load, the pins flex, allowing radial displacement of the planet gears. This displacement distributes forces evenly among the planet gears, compensating for manufacturing tolerances and reducing localized stress and gear wear."
    },
    {
        "id": "ME_2", "category": "Mechanical Engineering",
        "short": "Pneumatic cylinder actuator with integrated linear position sensor.",
        "medium": "A pneumatic cylinder actuator featuring an integrated linear position sensor. The piston rod contains magnetic markers. Hall effect sensors detect rod position to enable precision feedback control.",
        "long": "A pneumatic actuator featuring integrated closed-loop position feedback. The actuator comprises a cylinder housing, a piston, and a hollow piston rod. The inner surface of the hollow piston rod is embedded with magnetic strip markers showing alternating polarities. A Hall effect sensor array is mounted inside the cylinder housing on a stationary core rod extending into the hollow piston rod. As the piston rod extends, the sensors detect the magnetic fields, outputting quadrature signals. An internal microcontroller translates the signals into linear position measurements, enabling precision feedback control of pneumatic valves."
    },
    {
        "id": "ME_3", "category": "Mechanical Engineering",
        "short": "Hydraulic control valve with proportional solenoid and spool position feedback.",
        "medium": "A hydraulic control valve featuring a proportional solenoid and spool position feedback. An LVDT sensor measures spool displacement. A driver circuit adjusts solenoid currents to maintain flow rates.",
        "long": "A hydraulic control valve for high-precision flow regulation. The valve comprises a valve body, a sliding spool, and a proportional solenoid actuator. An electromagnetic linear variable differential transformer (LVDT) sensor is coupled to the valve spool to measure its displacement. A digital driver circuit receives flow command signals and spool position inputs from the LVDT. The driver adjusts the current fed to the solenoid using proportional-integral-derivative (PID) control algorithms, regulating spool position against hydraulic forces. This feedback loop eliminates spool hysteresis and improves valve response times."
    },
    {
        "id": "ME_4", "category": "Mechanical Engineering",
        "short": "Vibration isolation mount using elastomeric dampers and viscous fluid chambers.",
        "medium": "A vibration isolation mount featuring elastomeric dampers and viscous fluid chambers. The elastomeric body absorbs high-frequency vibrations. The fluid chambers dissipate low-frequency shocks through damping orifices.",
        "long": "A vibration isolation mount for industrial machinery. The mount comprises an outer housing, a central load-bearing member, and an elastomeric member connecting them. The interior of the elastomeric member features two fluid chambers filled with glycol-based viscous fluid, connected through a damping orifice. Under compression, the load-bearing member deforms the elastomeric member, forcing fluid between chambers. The viscous shear through the orifice dissipates low-frequency shocks. Simultaneously, the elastomeric body absorbs high-frequency vibrations, isolating the machinery from structural supports."
    },
    {
        "id": "ME_5", "category": "Mechanical Engineering",
        "short": "Centrifugal pump impeller design with backward swept blades to prevent cavitation.",
        "medium": "A centrifugal pump impeller featuring backward swept blades to prevent cavitation. The blades feature a variable inlet angle and contoured shroud. This geometry reduces localized pressure drops and improves hydraulic efficiency.",
        "long": "An impeller for a centrifugal pump designed to reduce cavitation and improve hydraulic efficiency. The impeller comprises a hub, a shroud, and multiple backward swept blades. The blades feature a variable inlet angle that matches the incoming fluid velocity vector, reducing entry losses. Additionally, the blade surface is contoured to maintain a gradual pressure transition along the flow channel, preventing localized pressure drops below the vapor pressure of the pumped fluid. Testing shows that this impeller geometry reduces cavitation damage and extends the operating life of the pump."
    },

    # 8. Energy
    {
        "id": "EN_1", "category": "Energy",
        "short": "Lithium-ion battery electrolyte composition containing fluorinated carbonate solvents.",
        "medium": "A lithium-ion battery electrolyte composition containing fluorinated carbonate solvents. The solvents form a stable solid electrolyte interphase. This layer improves capacity retention and high-voltage safety.",
        "long": "An electrolyte composition for high-voltage lithium-ion batteries. The composition comprises a lithium salt, such as lithium hexafluorophosphate, dissolved in a organic solvent mixture containing fluorinated cyclic and acyclic carbonate solvents. The solvent mixture includes fluoroethylene carbonate (FEC) and bis(2,2,2-trifluoroethyl) carbonate. During the initial charging cycle, the fluorinated solvents decompose on the anode surface, forming a thin, stable solid electrolyte interphase (SEI) layer containing lithium fluoride. This SEI layer prevents continuous electrolyte degradation, improving capacity retention and cycle life under high-voltage operation."
    },
    {
        "id": "EN_2", "category": "Energy",
        "short": "Maximum power point tracking algorithm for wind turbine generators using hill climbing.",
        "medium": "An MPPT algorithm for wind turbine generators utilizing hill climbing search. The controller monitors generator voltage and current. It adjusts rotor speeds dynamically to maximize power output.",
        "long": "A method for maximum power point tracking (MPPT) in variable-speed wind turbine systems. The system includes a wind turbine, a permanent magnet synchronous generator, and a power converter. The MPPT controller monitors generator voltage and current to calculate electrical power output. The controller applies a hill-climbing search algorithm, perturbing the rotor speed command and measuring the resulting power change. If the power increases, the speed is perturbed in the same direction; if it decreases, the direction is reversed. The algorithm tracks the maximum power point dynamically, adapting to changing wind speeds."
    },
    {
        "id": "EN_3", "category": "Energy",
        "short": "Solid oxide fuel cell stack design with internal reforming channels.",
        "medium": "A solid oxide fuel cell stack featuring internal steam reforming channels. The reforming channels utilize nickel catalysts. The design uses fuel cell heat to reform hydrocarbons directly inside the stack.",
        "long": "A solid oxide fuel cell (SOFC) stack design configured for internal reforming of hydrocarbon fuels. The stack comprises multiple planar cells, interconnects, and flow channels. The fuel flow channels are embedded with a nickel-alumina reforming catalyst. As natural gas and steam flow through the channels, the catalyst drives steam reforming reactions, converting methane to hydrogen and carbon monoxide. The endothermic reforming reaction absorbs heat generated by the electrochemical reactions of the fuel cell. This internal thermal integration reduces external reforming equipment, simplifies stack cooling, and increases energy conversion efficiency."
    },
    {
        "id": "EN_4", "category": "Energy",
        "short": "Flywheel energy storage system with magnetic bearings and vacuum housing.",
        "medium": "A flywheel energy storage system featuring magnetic bearings and a vacuum housing. The carbon-fiber rotor rotates on active magnetic bearings. The vacuum housing minimizes aerodynamic drag and idling losses.",
        "long": "A flywheel energy storage system for grid stabilization. The system comprises a carbon-fiber composite rotor, an integrated motor-generator, active magnetic bearings, and a sealed vacuum housing. The rotor is suspended vertically by the magnetic bearings, which are controlled by a digital feedback loop to maintain alignment. The motor-generator accelerates the rotor to store electrical energy as kinetic energy, and decelerates it to discharge power. The vacuum housing maintains a vacuum level below 10^-3 Torr, minimizing aerodynamic drag and self-discharge losses."
    },
    {
        "id": "EN_5", "category": "Energy",
        "short": "Biomass gasification reactor with secondary air injection to reduce tar content.",
        "medium": "A biomass gasification reactor featuring secondary air injection to reduce tar. The reactor introduces air into the combustion zone to promote cracking. This design produces a cleaner syngas suitable for power generation.",
        "long": "A downdraft biomass gasification reactor designed for clean syngas production. The reactor comprises a hopper, a drying zone, a pyrolysis zone, a combustion zone, and a reduction zone. The combustion zone features multiple primary air nozzles. Additionally, secondary air nozzles are positioned directly below the throat in the reduction zone. The secondary air injection initiates localized partial oxidation, raising temperatures to 1000 degrees Celsius and promoting thermal cracking of tar compounds. This tar cracking produces a syngas with low tar concentrations, reducing filtering requirements for downstream engine generators."
    },

    # 9. Auto
    {
        "id": "AT_1", "category": "Automotive",
        "short": "Electronic stability control system for hybrid vehicles using individual wheel torque.",
        "medium": "An electronic stability control system for hybrid vehicles utilizing individual wheel torque. The system monitors vehicle yaw rate and steering angle. It applies differential braking or motor torque to correct slides.",
        "long": "An electronic stability control (ESC) system for hybrid vehicles. The vehicle features an internal combustion engine and individual electric motors coupled to each wheel. The ESC system includes a sensor cluster that measures steering angle, wheel speeds, lateral acceleration, and yaw rate. An electronic control unit (ECU) calculates deviation differences between the steering input and the actual yaw rate. To correct understeer or oversteer, the ECU regulates the electric motors to apply differential torque to individual wheels, while applying selective hydraulic braking. This torque vectoring improves vehicle stability on low-friction surfaces."
    },
    {
        "id": "AT_2", "category": "Automotive",
        "short": "Active suspension actuator using electromagnetic linear motor.",
        "medium": "An active suspension actuator featuring an electromagnetic linear motor. The actuator adjusts wheel position based on forward-looking camera inputs. It isolates the vehicle body from road disturbances.",
        "long": "An active suspension system for passenger vehicles. The system comprises an electromagnetic linear motor actuator mounted in parallel with a spring at each wheel station. A forward-looking camera scans the road surface ahead, generating a profile. An electronic control unit processes the road profile and calculates the required actuator force. The linear motor applies forces to extend or contract the suspension, absorbing road bumps. This active control isolates the vehicle body from road disturbances, improving ride comfort and vehicle handling."
    },
    {
        "id": "AT_3", "category": "Automotive",
        "short": "Automated lane change assistance system using blind spot radar sensors.",
        "medium": "An automated lane change assistance system utilizing blind spot radar sensors. The system monitors adjacent lanes for vehicles. It controls steering actuators to execute lane changes safely when initiated.",
        "long": "An automated lane change system for autonomous vehicles. The vehicle is equipped with steering actuators and rear-facing radar sensors that monitor adjacent lanes. When a lane change is initiated, the radar sensors scan for approaching vehicles. An electronic control unit calculates the time-to-collision of approaching vehicles. If a safe gap is detected, the ECU sends command signals to the steering actuators to execute a lane change. If a vehicle enters the blind spot during the maneuver, the system aborts the change and returns the vehicle to its original lane."
    },
    {
        "id": "AT_4", "category": "Automotive",
        "short": "Dual-clutch transmission control system with adaptive slip synchronization.",
        "medium": "A dual-clutch transmission control system featuring adaptive slip synchronization. The controller monitors input shaft speeds during gear shifts. It regulates clutch pressure to transition torque smoothly.",
        "long": "A control system for a dual-clutch transmission in a passenger vehicle. The transmission includes an odd-gear clutch and an even-gear clutch. During a gear shift, an electronic control unit monitors input shaft speeds and clutch slip velocities. The ECU regulates hydraulic valves to adjust clutch clamping pressure. The pressure is controlled using adaptive algorithms that adjust to fluid temperature and clutch wear. This pressure regulation ensures a smooth overlap of clutch engagements, transitioning torque between shafts without power interruption or shift shock."
    },
    {
        "id": "AT_5", "category": "Automotive",
        "short": "Regenerative braking control method for electric vehicles based on deceleration demand.",
        "medium": "A regenerative braking control method for electric vehicles. The controller monitors brake pedal stroke and calculates deceleration demand. It blends regenerative braking with hydraulic braking to optimize energy recovery.",
        "long": "A regenerative braking control system for electric vehicles. The system includes an electric motor-generator, a friction braking system, and a brake pedal sensor. The sensor measures brake pedal stroke and pressure to calculate deceleration demand. An electronic control unit determines the maximum available regenerative braking torque based on battery state-of-charge and motor speed. The ECU commands the motor-generator to apply regenerative braking torque, and regulates the friction brakes to supply any remaining demand. This braking blend maximizes kinetic energy recovery during deceleration while maintaining braking feel."
    },

    # 10. Cyber
    {
        "id": "CY_1", "category": "Cybersecurity",
        "short": "Intrusion detection system using deep packet inspection and signature matching.",
        "medium": "An intrusion detection system utilizing deep packet inspection and signature matching. The system reassembles network packets in memory. It matches payloads against database signatures to identify threats.",
        "long": "An intrusion detection system (IDS) for enterprise networks. The IDS is connected to a network switch to capture incoming and outgoing packets. The device includes a packet parser that reassembles packets in memory to reconstruct application-layer payloads. A signature matching engine matches the payloads against a signature database containing patterns of known exploits and malware signatures. The matching engine applies parallel search algorithms, using bit-parallel techniques, to analyze payloads without reducing network throughput. If a match is detected, the IDS logs the event and sends alert notifications to security administrators."
    },
    {
        "id": "CY_2", "category": "Cybersecurity",
        "short": "Secure cryptographic key distribution protocol using quantum entanglement.",
        "medium": "A cryptographic key distribution protocol utilizing quantum entanglement. The system generates and distributes entangled photon pairs. Eavesdropping attempts alter photon states, exposing the security breach.",
        "long": "A quantum key distribution (QKD) system and protocol for secure cryptographic key exchange. The system comprises a transmitter, a receiver, and a fiber-optic channel connecting them. The transmitter generates entangled photon pairs and sends one photon from each pair to the receiver. The transmitter and receiver measure the polarization states of their photons using randomly selected bases. By comparing a subset of their measurements, they establish a shared secret key. If an eavesdropper attempts to intercept the photons, the quantum states are altered, introducing anomalies that are detected by the system, ensuring security."
    },
    {
        "id": "CY_3", "category": "Cybersecurity",
        "short": "Automated vulnerability scanner for web applications using dynamic fuzzing.",
        "medium": "An automated vulnerability scanner for web applications utilizing dynamic fuzzing. The scanner generates anomalous input payloads. It monitors application responses to identify injection vulnerabilities.",
        "long": "An automated security scanner for identifying vulnerabilities in web applications. The scanner includes a crawler that maps the directory structure and input forms of a target application. A fuzzing engine generates input payloads, including SQL injection strings and cross-site scripting (XSS) scripts, and submits them to the input forms. The scanner monitors application responses, checking for SQL error messages or reflected script outputs. If an input causes anomalous behavior or exposes sensitive files, the scanner logs the vulnerability, generating a report with remediation recommendations."
    },
    {
        "id": "CY_4", "category": "Cybersecurity",
        "short": "Secure multi-factor authentication method using dynamic QR code challenge.",
        "medium": "A multi-factor authentication method featuring dynamic QR code challenges. The login screen displays a time-varying QR code containing an encrypted challenge. A smartphone app decrypts the challenge to verify user identity.",
        "long": "A secure multi-factor authentication system. During login, a server generates a time-varying challenge containing an encrypted token. The challenge is rendered as a dynamic QR code on the user's login screen. The user scans the QR code using a registered smartphone application. The application decrypts the token, signs it with a private cryptographic key stored in the phone's secure element, and transmits the signed token back to the authentication server over a cellular connection. The server verifies the signature, authorizing the login session without requiring password entry."
    },
    {
        "id": "CY_5", "category": "Cybersecurity",
        "short": "Zero-trust network access control system using continuous risk scoring.",
        "medium": "A zero-trust access control system utilizing continuous risk scoring. The system monitors device compliance, login times, and data access patterns. It adjusts user privileges dynamically based on risk updates.",
        "long": "A zero-trust network access (ZTNA) control system. The system interfaces with enterprise directory servers and firewall gateways to regulate user access to applications. An evaluation engine monitors access sessions, calculating a dynamic risk score based on parameters including device patch compliance, login times, and data access volumes. If the risk score exceeds a safety threshold, the system restricts access privileges, requiring additional authentication challenges or terminating the session. This continuous access evaluation ensures that credentials do not grant access if device security is compromised."
    }
]

def jaccard_similarity(list1, list2):
    s1, s2 = set(list1), set(list2)
    union = s1.union(s2)
    return len(s1.intersection(s2)) / len(union) if union else 0.0

def compute_intradoc_similarity(results, db_path):
    """
    Computes the average pairwise cosine similarity between retrieved document texts.
    This tells us how redundant the result set is.
    """
    if len(results) <= 1:
        return 1.0
        
    # Lazy initialize model
    model, _ = get_retrieval_resources(db_path)
    
    texts = [res["patent_text"] for res in results]
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    
    # Calculate pairwise similarities
    # Normalise embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norm_embeddings = embeddings / norms
    
    similarity_matrix = np.dot(norm_embeddings, norm_embeddings.T)
    
    # Extract upper triangle values (excluding diagonal)
    tri_indices = np.triu_indices_from(similarity_matrix, k=1)
    pairwise_similarities = similarity_matrix[tri_indices]
    
    return float(np.mean(pairwise_similarities))

def is_domain_aligned(query_cat, patent_field):
    """
    Checks if query category aligns with the patent's field_of_invention.
    """
    mapping = {
        "AI": ["COMPUTER SCIENCE", "ELECTRONICS", "ELECTRICAL", "COMMUNICATION", "PHYSICS"],
        "Healthcare": ["BIO-MEDICAL ENGINEERING", "PHARMACEUTICALS", "PHYSICS", "MECHANICAL ENGINEERING", "GENERAL ENGINEERING"],
        "Biotechnology": ["BIOTECHNOLOGY", "MICRO BIOLOGY", "TRADITIONAL KNOWLEDGE BIOTECHNOLOGY", "PHARMACEUTICALS", "CHEMICAL"],
        "Communication": ["COMMUNICATION", "ELECTRICAL", "ELECTRONICS", "COMPUTER SCIENCE"],
        "Computer Science": ["COMPUTER SCIENCE", "ELECTRICAL", "ELECTRONICS", "COMMUNICATION"],
        "Electronics": ["ELECTRONICS", "ELECTRICAL", "COMPUTER SCIENCE", "PHYSICS"],
        "Mechanical Engineering": ["MECHANICAL ENGINEERING", "GENERAL ENGINEERING", "CIVIL", "METALLURGY", "TEXTILE"],
        "Energy": ["ELECTRICAL", "PHYSICS", "CHEMICAL", "MECHANICAL ENGINEERING", "GENERAL ENGINEERING"],
        "Automotive": ["MECHANICAL ENGINEERING", "ELECTRICAL", "ELECTRONICS", "GENERAL ENGINEERING"],
        "Cybersecurity": ["COMPUTER SCIENCE", "ELECTRONICS", "COMMUNICATION", "ELECTRICAL"]
    }
    
    allowed = mapping.get(query_cat, [])
    return patent_field in allowed

def main():
    print("==================================================")
    print("PatentIQ - Running Phase 3.5 Retrieval Stress Test")
    print(f"Total Test Inventions : {len(INVENTIONS)}")
    print("==================================================")

    db_path = "data/vectordb"
    stress_report_path = os.path.join("backend", "reports", "stress_test_report.txt")
    readiness_report_path = os.path.join("backend", "reports", "rag_readiness_audit.txt")

    os.makedirs(os.path.dirname(stress_report_path), exist_ok=True)

    # 1. Warm up resources
    print("Warming up model and ChromaDB client...")
    get_retrieval_resources(db_path)

    # Metrics collections
    latencies = {"short": [], "medium": [], "long": []}
    relevance_scores = {"short": [], "medium": [], "long": []}
    domain_alignments = {"short": [], "medium": [], "long": []}
    intradoc_similarities = {"short": [], "medium": [], "long": []}
    
    # Store retrieved document IDs to compute overlaps
    retrieved_ids = {
        "short": {},
        "medium": {},
        "long": {}
    }

    # Query loop
    print("\nRunning stress test on all 150 query profiles...")
    
    for idx, inv in enumerate(INVENTIONS):
        inv_id = inv["id"]
        cat = inv["category"]
        
        # Test each length profile
        for length in ["short", "medium", "long"]:
            query_text = inv[length]
            
            start_time = time.time()
            try:
                # Query top-20 for comprehensive overlap analysis
                results = semantic_search(query_text, top_k=20, db_path=db_path)
            except Exception as e:
                print(f"[ERROR] Query failed for {inv_id} ({length}): {e}")
                sys.exit(1)
                
            latency = time.time() - start_time
            latencies[length].append(latency)
            
            # Store IDs for Top-5, Top-10, Top-20
            retrieved_ids[length][inv_id] = {
                5: [res["application_number"] for res in results[:5]],
                10: [res["application_number"] for res in results[:10]],
                20: [res["application_number"] for res in results[:20]]
            }
            
            # 1. Relevance: Mean of top-5 similarities
            if results:
                top_5_scores = [res["similarity_score"] for res in results[:5]]
                relevance_scores[length].append(np.mean(top_5_scores))
                
                # 2. Domain Alignment: Check if top retrieved maps to query category
                top_1_field = results[0]["field_of_invention"]
                domain_alignments[length].append(1 if is_domain_aligned(cat, top_1_field) else 0)
                
                # 3. Diversity: Intradoc similarity of Top-5
                intradoc_sim = compute_intradoc_similarity(results[:5], db_path)
                intradoc_similarities[length].append(intradoc_sim)
            else:
                relevance_scores[length].append(0.0)
                domain_alignments[length].append(0)
                intradoc_similarities[length].append(1.0)
                
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(INVENTIONS)} inventions...")

    # Calculate Jaccard Overlaps (Consistency)
    overlaps_s_m = {5: [], 10: [], 20: []}
    overlaps_s_l = {5: [], 10: [], 20: []}
    overlaps_m_l = {5: [], 10: [], 20: []}
    
    for inv in INVENTIONS:
        inv_id = inv["id"]
        for k in [5, 10, 20]:
            ids_s = retrieved_ids["short"][inv_id][k]
            ids_m = retrieved_ids["medium"][inv_id][k]
            ids_l = retrieved_ids["long"][inv_id][k]
            
            overlaps_s_m[k].append(jaccard_similarity(ids_s, ids_m))
            overlaps_s_l[k].append(jaccard_similarity(ids_s, ids_l))
            overlaps_m_l[k].append(jaccard_similarity(ids_m, ids_l))

    # Compute averages
    mean_latencies = {l: np.mean(latencies[l]) * 1000 for l in ["short", "medium", "long"]}
    mean_relevance = {l: np.mean(relevance_scores[l]) for l in ["short", "medium", "long"]}
    mean_alignment = {l: np.mean(domain_alignments[l]) for l in ["short", "medium", "long"]}
    mean_diversity = {l: np.mean(intradoc_similarities[l]) for l in ["short", "medium", "long"]}
    
    mean_overlaps = {
        "short_vs_medium": {k: np.mean(overlaps_s_m[k]) for k in [5, 10, 20]},
        "short_vs_long": {k: np.mean(overlaps_s_l[k]) for k in [5, 10, 20]},
        "medium_vs_long": {k: np.mean(overlaps_m_l[k]) for k in [5, 10, 20]}
    }

    # Failure Analysis: Identify queries with weak relevance (<0.52) or low consistency (Jaccard S vs L @ Top-5 < 0.35)
    failures = []
    for idx, inv in enumerate(INVENTIONS):
        inv_id = inv["id"]
        cat = inv["category"]
        
        rel_s = relevance_scores["short"][idx]
        rel_l = relevance_scores["long"][idx]
        jac_s_l = jaccard_similarity(retrieved_ids["short"][inv_id][5], retrieved_ids["long"][inv_id][5])
        
        if rel_l < 0.52 or jac_s_l < 0.35:
            failures.append({
                "id": inv_id,
                "category": cat,
                "short_query": inv["short"][:80] + "...",
                "long_relevance": rel_l,
                "jaccard_consistency": jac_s_l,
                "reason": "Context dilution" if rel_l < rel_s else "Semantic drift"
            })

    # RAG Readiness Score Calculation
    # Weights: Relevance (30%), Consistency (30%), Domain Alignment (20%), Diversity (10%), Latency (10%)
    # Normalized parameters out of 100
    w_relevance = mean_relevance["long"] * 100  # Target: 0.60+ -> 60 points mapped to scale
    w_consistency = mean_overlaps["short_vs_long"][5] * 100 # Target: 0.50+ -> 50 points mapped
    w_alignment = mean_alignment["long"] * 100 # Target: 80%+
    w_diversity = (1.0 - mean_diversity["long"]) * 100 # Intradoc similarity around 0.30 -> (1 - 0.30)*100 = 70 points
    w_latency = max(0.0, 100.0 - mean_latencies["long"]) # Latency under 50ms -> 50+ points
    
    # Scale scores to standard scale
    score_relevance = min(100.0, w_relevance / 0.65 * 100)
    score_consistency = min(100.0, w_consistency / 0.55 * 100)
    score_alignment = w_alignment
    score_diversity = min(100.0, w_diversity / 0.75 * 100)
    score_latency = w_latency
    
    rag_readiness_score = (
        (score_relevance * 0.30) +
        (score_consistency * 0.30) +
        (score_alignment * 0.20) +
        (score_diversity * 0.10) +
        (score_latency * 0.10)
    )

    # 2. Write reports
    print(f"\nSaving Stress Test Report to: {stress_report_path}")
    with open(stress_report_path, "w") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - Retrieval Stress Test Report\n")
        f.write("==================================================\n\n")
        f.write("Performance and Metric Breakdown by Query Length:\n")
        f.write("--------------------------------------------------\n")
        for length in ["short", "medium", "long"]:
            f.write(f"Query Profile: {length.upper()}\n")
            f.write(f"  Average Latency        : {mean_latencies[length]:.2f} ms\n")
            f.write(f"  Average Similarity     : {mean_relevance[length]:.4f}\n")
            f.write(f"  Domain Match Rate      : {mean_alignment[length]*100:.2f}%\n")
            f.write(f"  Intradoc Similarity    : {mean_diversity[length]:.4f}\n\n")
            
        f.write("Query Length Consistency (Jaccard Overlap):\n")
        f.write("--------------------------------------------------\n")
        for comparison, metrics in mean_overlaps.items():
            f.write(f"Comparison: {comparison.replace('_', ' ').upper()}\n")
            f.write(f"  Jaccard Overlap @ Top-5  : {metrics[5]:.4f}\n")
            f.write(f"  Jaccard Overlap @ Top-10 : {metrics[10]:.4f}\n")
            f.write(f"  Jaccard Overlap @ Top-20 : {metrics[20]:.4f}\n\n")
        f.write("==================================================\n")

    print(f"Saving RAG Readiness Audit to: {readiness_report_path}")
    with open(readiness_report_path, "w") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - RAG Readiness Audit Report\n")
        f.write("==================================================\n\n")
        f.write(f"RAG Readiness Score: {rag_readiness_score:.2f} / 100\n")
        f.write(f"RAG Readiness Decision: {'YES' if rag_readiness_score >= 75 else 'NO'}\n\n")
        
        f.write("Scoring Component Breakdown:\n")
        f.write(f"  1. Semantic Relevance (30% weight) : {score_relevance:.2f} / 100\n")
        f.write(f"  2. Length Consistency (30% weight) : {score_consistency:.2f} / 100\n")
        f.write(f"  3. Domain Alignment   (20% weight) : {score_alignment:.2f} / 100\n")
        f.write(f"  4. Result Diversity   (10% weight) : {score_diversity:.2f} / 100\n")
        f.write(f"  5. Latency Score      (10% weight) : {score_latency:.2f} / 100\n\n")
        
        f.write("Failure Analysis Checklist:\n")
        f.write(f"  Total Anomalous/Weak Queries Detected: {len(failures)}\n")
        f.write("--------------------------------------------------\n")
        if failures:
            for fail in failures:
                f.write(f"Query ID: {fail['id']} | Category: {fail['category']}\n")
                f.write(f"  Text: {fail['short_query']}\n")
                f.write(f"  Long Relevance: {fail['long_relevance']:.4f} | Jaccard Overlap: {fail['jaccard_consistency']:.4f}\n")
                f.write(f"  Failure Diagnosis: {fail['reason']}\n")
                f.write(f"  Explanation: Long-form technical jargon diluted the key semantic concept, leading to attention shifts.\n\n")
        else:
            f.write("  Zero failures detected. All queries met thresholds.\n")
        f.write("==================================================\n")

    print("\nStress test and RAG audit run completed successfully!")
    print("==================================================")

if __name__ == '__main__':
    main()
