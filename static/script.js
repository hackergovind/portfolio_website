document.addEventListener('DOMContentLoaded', () => {
    
    // --- Theme Toggling ---
    const html = document.documentElement;
    const themeBtn = document.getElementById('theme-btn');
    const sunIcon = document.querySelector('.sun-icon');
    const moonIcon = document.querySelector('.moon-icon');

    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);

    themeBtn.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    }

    // --- Scroll Animations ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.scroll-animate').forEach(el => observer.observe(el));

    // --- Typing Effect ---
    const typingText = document.getElementById('typing-text');
    const words = ["I'm a Backend Developer", "I'm a Security Analyst"];
    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typeDelay = 100;

    function type() {
        if (!typingText) return;
        const currentWord = words[wordIndex];
        
        if (isDeleting) {
            typingText.textContent = currentWord.substring(0, charIndex - 1);
            charIndex--;
            typeDelay = 50;
        } else {
            typingText.textContent = currentWord.substring(0, charIndex + 1);
            charIndex++;
            typeDelay = 150;
        }

        if (!isDeleting && charIndex === currentWord.length) {
            isDeleting = true;
            typeDelay = 1500; // Pause at end of word
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
            typeDelay = 500; // Pause before next word
        }

        setTimeout(type, typeDelay);
    }
    setTimeout(type, 1000); // Initial delay

    // --- Interactive Terminal ---
    const terminalInput = document.getElementById('terminal-input');
    const terminalBody = document.getElementById('terminal-body');

    if (terminalInput && terminalBody) {
        const commands = {
            'whoami': `Govind Pratap Singh — Security Engineer & Python/FastAPI Backend Developer\n"Securing backend systems with Python/FastAPI & Ethical Hacking"`,
            'skills': `Security: Web/API/Mobile VAPT, OWASP Top 10, Burp Suite, Nmap\nSOC: SIEM, Incident Response, Threat Hunting, MITRE ATT&CK\nBackend: Python, FastAPI, Django, PostgreSQL, Redis, Docker, WebSockets`,
            'cve': `CVE-2025-61246 (CVSS 9.8 — Critical)\nSQL Injection Vulnerability\nFull PoC: [Link]\nDocker Lab: [Link]\nRemediation Guide: [Link]`,
            'nasa': `🏆 NASA VDP Hall of Fame\nResponsibly disclosed vulnerabilities in NASA's public-facing infrastructure\nLink: https://bugcrowd.com/disclosures/121d979a-b47e-4b70-b464-eb6d0013a52b`,
            'projects': `1. CVE Radar — Threat Intelligence Platform (cve-radar.nx.kg)\n2. AutoRecon — Reconnaissance Framework (github.com/hackergovind/autorecon)\n3. Secure REST API with FastAPI + PostgreSQL + Redis\n4. Vulnerability Tracker API (Django REST + Celery)\n5. Real-Time Threat Feed (FastAPI + WebSockets + Redis)\n6. DevSecOps CI/CD Pipeline (GitHub Actions + Jenkins + Docker)`,
            'python': `🐍 Python/FastAPI Backend Expertise:\n• Python 3.12+ | FastAPI | Django\n• Django REST Framework | Pydantic v2\n• REST APIs | WebSockets | Async/Await\n• SQLAlchemy | PostgreSQL | Redis\n• Docker | Kubernetes | CI/CD\n• GitHub Actions | Jenkins | Cloud Deployment`,
            'security': `🔐 Cybersecurity Expertise:\n• Web/API/Mobile Penetration Testing\n• Vulnerability Assessment & Remediation\n• OWASP Top 10 | MITRE ATT&CK\n• Threat Modeling | Risk Assessment\n• Burp Suite | Nmap | Metasploit | Nessus\n• CVE Research | Exploit Development`,
            'soc': `🔐 Security Operations (SOC) Knowledge:\n• SIEM: Splunk, ELK Stack basics (log analysis, alert triage)\n• Incident Response: Detection → Containment → Eradication → Recovery\n• Threat Hunting: Proactive searching for IoCs\n• IDS/IPS: Snort, Suricata (rule analysis)\n• Frameworks: MITRE ATT&CK, NIST CSF, Cyber Kill Chain\n• Tools: Wireshark, Sysinternals, OSQuery\nPractical exposure via:\n→ TryHackMe SOC Level 1 Labs (50+ rooms)\n→ Google Cybersecurity Certification (SIEM, IR, NIST)`,
            'experience': `Cybersecurity Intern (VAPT) | Ceeras IT Services | Feb-June 2025\n• 8+ production apps tested\n• 15+ vulnerabilities found (SQLi, XSS, IDOR)\n• 8+ pentest reports authored with CVSS scoring\n• Complete VAPT lifecycle (recon → reporting → validation)`,
            'contact': window.dynamicContact || `📧 govindsinghpratap123@gmail.com\n📱 +91 6396448562\n🔗 linkedin.com/in/govindpratapsingh404\n🐙 github.com/hackergovind\n📝 medium.com/@hackergovind`,
            'resume': `📄 Downloading Resume (Opening in new tab)...`,
            'help': `Available commands: whoami, skills, cve, nasa, projects, python, security, soc, experience, contact, resume, clear, help`
        };

        terminalInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const input = this.value.trim().toLowerCase();
                this.value = '';

                // Echo the command
                const echoLine = document.createElement('div');
                echoLine.className = 'terminal-line';
                echoLine.innerHTML = `<span class="prompt">govind@portfolio:~$</span> ${input}`;
                terminalBody.appendChild(echoLine);

                if (input === 'clear') {
                    // Keep the welcome message but clear the rest
                    terminalBody.innerHTML = `<div class="terminal-line"><span class="prompt">govind@portfolio:~$</span> <span class="typing">Welcome to Govind's Portfolio Shell v1.0.0</span></div>`;
                    return;
                }

                if (input !== '') {
                    const response = commands[input] || `bash: ${input}: command not found`;
                    const responseLine = document.createElement('div');
                    responseLine.className = 'terminal-line';
                    responseLine.innerText = response;
                    terminalBody.appendChild(responseLine);

                    if (input === 'resume') {
                        setTimeout(() => window.open('resume.html', '_blank'), 500);
                    }
                }

                // Scroll to bottom
                terminalBody.scrollTop = terminalBody.scrollHeight;
            }
        });
        
        // Focus terminal input when clicking anywhere in the terminal body
        terminalBody.addEventListener('click', () => {
            terminalInput.focus();
        });
    }

    // --- Contact Form ---
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = contactForm.querySelector('button');
            const originalText = btn.innerText;
            btn.innerText = 'Sending...';
            
            // Simulate form submission
            setTimeout(() => {
                btn.innerText = 'Message Sent!';
                btn.style.backgroundColor = '#27c93f';
                btn.style.color = '#000';
                contactForm.reset();
                
                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.style.backgroundColor = '';
                    btn.style.color = '';
                }, 3000);
            }, 1000);
        });
    }
});
