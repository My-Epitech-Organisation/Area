import React from 'react';
import { Link } from 'react-router-dom';

const Privacy: React.FC = () => {
  return (
    <div className="w-screen min-h-screen bg-page-about flex flex-col items-center">
      <header className="w-full pt-28 flex justify-center">
        <h1 className="text-5xl font-bold text-theme-primary mb-8">Privacy Policy</h1>
      </header>
      <main className="w-full max-w-4xl px-8 pb-16 flex-1 flex flex-col text-left">
        <p className="text-theme-muted mb-8">
          <strong>Last updated:</strong> November 1, 2025
        </p>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            1. Information We Collect
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            AREA collects information you provide when connecting third-party services through OAuth
            authentication. This includes OAuth tokens that allow us to interact with services like
            Notion, GitHub, Gmail, Slack, Spotify, Twitch, and others on your behalf.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            We also collect basic account information (email address, username) to create and
            manage your AREA account.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            2. How We Use Your Information
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We use your information solely to:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Execute the automations (areactions) you configure</li>
            <li>Connect to third-party APIs on your behalf using your OAuth tokens</li>
            <li>Send notifications when your automations trigger</li>
            <li>Provide, maintain, and improve our service</li>
            <li>Communicate with you about service updates or issues</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            We <strong>never</strong> sell your data to third parties or use it for advertising
            purposes.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            3. Data Security
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            Your OAuth tokens and sensitive information are encrypted and stored securely in our
            database. We use industry-standard security practices including:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>HTTPS/TLS encryption for all data in transit</li>
            <li>Encrypted storage of OAuth tokens and credentials</li>
            <li>Secure authentication using JWT (JSON Web Tokens)</li>
            <li>Regular security audits and updates</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            4. Data Sharing
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We do not share your personal data with third parties except:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>
              When necessary to execute your configured automations (e.g., sending a Slack message
              via Slack&apos;s API)
            </li>
            <li>When required by law or to protect our legal rights</li>
            <li>With your explicit consent</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">5. Your Rights</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            You have the right to:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Access your personal data</li>
            <li>Disconnect any connected service at any time</li>
            <li>Delete your account and all associated data</li>
            <li>Export your automation configurations</li>
            <li>Request correction of inaccurate data</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            You can manage your connected services and automations through your{' '}
            <Link to="/profile" className="text-theme-accent hover:underline">
              profile page
            </Link>
            .
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">6. Data Retention</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We retain your data for as long as your account is active. When you delete your account:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>All OAuth tokens are immediately revoked and deleted</li>
            <li>Your automations and configurations are permanently removed</li>
            <li>Personal information is deleted within 30 days</li>
            <li>Anonymized usage logs may be retained for security purposes</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            7. Cookies and Tracking
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We use essential cookies to:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Maintain your login session</li>
            <li>Remember your preferences</li>
            <li>Ensure security and prevent fraud</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            We do not use third-party tracking cookies or analytics beyond basic server logs.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            8. Changes to This Policy
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We may update this Privacy Policy from time to time. We will notify you of any
            significant changes by email or through a notice on our website. Your continued use of
            AREA after changes are posted constitutes acceptance of the updated policy.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">9. Contact Us</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            For privacy questions or concerns, please contact us at:
          </p>
          <p className="text-lg text-theme-accent mt-4">
            <a href="mailto:admin@areaction.app" className="hover:underline">
              admin@areaction.app
            </a>
          </p>
        </section>

        <div className="mt-12 pt-8 border-t border-theme-surface">
          <Link
            to="/"
            className="text-theme-accent hover:text-theme-primary transition-colors font-medium"
          >
            ← Back to Home
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Privacy;
