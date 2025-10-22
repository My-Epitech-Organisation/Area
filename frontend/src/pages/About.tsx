import React from 'react';
import nolanPapa from '../assets/nolan_papa.jpg';
import paulAntoineSalmon from '../assets/paul_antoine_salmon.jpg';
import maelPerrigaud from '../assets/mael_perrigaud.png';
import santiagoPidcova from '../assets/santiago_pidcova.png';
import matheoCoquet from '../assets/matheo_coquet.png';

const About: React.FC = () => {
  return (
    <div className="w-screen min-h-screen bg-page-about flex flex-col items-center">
      <header className="w-full pt-28 flex justify-center">
        <h1 className="text-5xl font-bold text-theme-primary mb-8">About AREA</h1>
      </header>
      <main className="w-full max-w-4xl px-8 flex-1 flex flex-col items-center text-center">
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">What is AREA?</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            AREA is an innovative platform designed to revolutionize your workflow by creating
            automated actions, or &quot;areactions,&quot; through seamless integration with popular
            services like Google, GitHub, Microsoft Teams, and more. Whether you&apos;re a
            developer, student, or productivity enthusiast, AREA empowers you to connect your
            favorite tools and automate repetitive tasks effortlessly.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            Born from a student project, AREA is not just a tool—it&apos;s a vision for smarter,
            more connected digital experiences. We&apos;re passionate about making technology work
            for you, one automation at a time.
          </p>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">How AREA Works</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            AREA operates on a simple yet powerful principle:{' '}
            <strong>&quot;if this, then that&quot;</strong>. Users create automated workflows by
            connecting triggers (events that start an action) with reactions (the automated
            responses). For example, you can set up a workflow where receiving a new email triggers
            a notification on your phone, or a new GitHub issue automatically creates a task in your
            project management tool.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            Our platform provides an intuitive interface where you can browse available services,
            select triggers and actions, and configure your custom automations in minutes. &quot;No
            coding required &ndash; just connect, configure, and let AREA handle the rest.&quot;
          </p>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">Supported Services</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            AREA integrates with a growing ecosystem of popular services to give you maximum
            flexibility in your automations. Our current supported services include:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-6">
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">Google Services</p>
              <p className="text-theme-muted text-sm">Gmail, Calendar, Drive</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">GitHub</p>
              <p className="text-theme-muted text-sm">Repositories, Issues, PRs</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">Microsoft Teams</p>
              <p className="text-theme-muted text-sm">Messages, Channels</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">Discord</p>
              <p className="text-theme-muted text-sm">Channels, Messages</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">Spotify</p>
              <p className="text-theme-muted text-sm">Playlists, Tracks</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">Weather APIs</p>
              <p className="text-theme-muted text-sm">Weather triggers</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">Timer</p>
              <p className="text-theme-muted text-sm">Scheduled actions</p>
            </div>
            <div className="bg-theme-surface p-4 rounded-lg text-center">
              <p className="text-theme-primary font-medium">And more...</p>
              <p className="text-theme-muted text-sm">Continuously expanding</p>
            </div>
          </div>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            Understanding Areactions
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            &quot;Areactions&quot; are the heart of AREA – custom automated workflows that you
            create. Each areaction consists of three main components:
          </p>
          <ul className="text-left text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>
              <strong className="text-theme-primary">Trigger:</strong> The event that initiates the
              automation (e.g., &quot;When I receive a new email&quot;)
            </li>
            <li>
              <strong className="text-theme-primary">Condition:</strong> Optional filters to refine
              when the action should occur (e.g., &quot;Only if the email is from my boss&quot;)
            </li>
            <li>
              <strong className="text-theme-primary">Action:</strong> The automated response (e.g.,
              &quot;Send me a notification on my phone&quot;)
            </li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            Areactions can be simple (one trigger, one action) or complex (multiple conditions and
            chained actions). You can create as many as you need, and they&apos;re all managed
            through your personal dashboard.
          </p>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">Our Mission</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            At AREA, our mission is to democratize automation. We believe that powerful automation
            tools shouldn&apos;t be limited to enterprises or technical experts. By providing an
            accessible, user-friendly platform, we empower everyone – from students to professionals
            – to streamline their digital lives and focus on what truly matters.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            We&apos;re committed to privacy, security, and open-source principles. Your data stays
            yours, and we continuously work to expand our service integrations while maintaining the
            highest standards of reliability and user experience.
          </p>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">Looking Ahead</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            As a student-led project, AREA is constantly evolving. We&apos;re working on exciting
            features like advanced workflow templates, AI-powered automation suggestions, mobile app
            enhancements, and integration with even more services. Our roadmap is driven by user
            feedback and our passion for innovation.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            Join us on this journey to make automation accessible to everyone. Your feedback and
            contributions help shape the future of AREA.
          </p>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-8">Meet the Team</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8 w-full max-w-7xl mx-auto">
            <div className="bg-theme-surface p-6 rounded-lg shadow-lg flex flex-col items-center">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4">
                <img src={nolanPapa} alt="Nolan PAPA" className="w-full h-full object-cover" />
              </div>
              <h3 className="text-xl font-bold text-theme-primary mb-2">Nolan PAPA</h3>
              <p className="text-theme-muted">Lead Developer frontend</p>
            </div>
            <div className="bg-theme-surface p-6 rounded-lg shadow-lg flex flex-col items-center">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4">
                <img
                  src={paulAntoineSalmon}
                  alt="Paul-Antoine SALMON"
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-xl font-bold text-theme-primary mb-2">Paul-Antoine SALMON</h3>
              <p className="text-theme-muted">Lead Developer backend</p>
            </div>
            <div className="bg-theme-surface p-6 rounded-lg shadow-lg flex flex-col items-center">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4">
                <img
                  src={maelPerrigaud}
                  alt="Mael Perrigaud"
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-xl font-bold text-theme-primary mb-2">Mael Perrigaud</h3>
              <p className="text-theme-muted">Lead Developer mobile</p>
            </div>
            <div className="bg-theme-surface p-6 rounded-lg shadow-lg flex flex-col items-center">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4">
                <img
                  src={santiagoPidcova}
                  alt="Santiago Pidcova"
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-xl font-bold text-theme-primary mb-2">Santiago Pidcova</h3>
              <p className="text-theme-muted">Full-stack Developer & Project Coordinator</p>
            </div>
            <div className="bg-theme-surface p-6 rounded-lg shadow-lg flex flex-col items-center">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4">
                <img
                  src={matheoCoquet}
                  alt="Matheo Coquet"
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-xl font-bold text-theme-primary mb-2">Matheo Coquet</h3>
              <p className="text-theme-muted">trainee developer</p>
            </div>
          </div>
        </section>
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">Get in Touch</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            Have questions, suggestions, or just want to chat about AREA? Reach out to us at{' '}
            <a href="mailto:area@contact.com" className="text-theme-link text-theme-link-hover">
              area@contact.com
            </a>
            .
          </p>
        </section>
      </main>
    </div>
  );
};

export default About;
