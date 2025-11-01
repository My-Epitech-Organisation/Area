import React from 'react';
import { Link } from 'react-router-dom';

const Terms: React.FC = () => {
  return (
    <div className="w-screen min-h-screen bg-page-about flex flex-col items-center">
      <header className="w-full pt-28 flex justify-center">
        <h1 className="text-5xl font-bold text-theme-primary mb-8">Terms of Use</h1>
      </header>
      <main className="w-full max-w-4xl px-8 pb-16 flex-1 flex flex-col text-left">
        <p className="text-theme-muted mb-8">
          <strong>Last updated:</strong> November 1, 2025
        </p>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">1. Acceptance of Terms</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            By accessing or using AREA (&quot;the Service&quot;), you agree to be bound by these
            Terms of Use. If you do not agree to these terms, please do not use our service.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            These terms constitute a legally binding agreement between you and AREA. By creating an
            account, you represent that you are at least 13 years old and have the legal capacity to
            enter into this agreement.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">2. Service Description</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            AREA is an automation platform that enables users to create workflows
            (&quot;areactions&quot;) by connecting various third-party services including but not
            limited to:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Notion (pages, databases, blocks)</li>
            <li>GitHub (repositories, issues, pull requests)</li>
            <li>Gmail and Google Calendar</li>
            <li>Slack (messages, channels)</li>
            <li>Spotify (playlists, tracks)</li>
            <li>Twitch (streams, clips)</li>
            <li>Weather services</li>
            <li>Custom webhooks and timers</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            The Service allows you to define triggers (actions) that, when activated, execute
            automated responses (reactions) across connected services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            3. User Responsibilities
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">You agree to:</p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Provide accurate and complete registration information</li>
            <li>Maintain the security of your account credentials</li>
            <li>Comply with all applicable laws and regulations when using the Service</li>
            <li>Respect the terms of service of all third-party services you connect to AREA</li>
            <li>Not use the Service for illegal activities, spam, harassment, or abuse</li>
            <li>Not attempt to gain unauthorized access to other users&apos; accounts or data</li>
            <li>Not overload our systems with excessive API requests or automations</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            4. OAuth and Third-Party Services
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            When you connect a third-party service via OAuth:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>
              You grant AREA permission to access that service on your behalf using the scopes you
              authorize
            </li>
            <li>
              You remain responsible for your use of those third-party services and must comply with
              their respective terms
            </li>
            <li>
              AREA is not responsible for changes, outages, or discontinuation of third-party
              services
            </li>
            <li>You can revoke access at any time through your profile settings</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            5. Service Availability
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We strive to maintain 99% uptime for the Service, but we do not guarantee uninterrupted
            or error-free operation. The Service may be temporarily unavailable due to:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Scheduled maintenance</li>
            <li>Emergency repairs or security updates</li>
            <li>Third-party API outages or rate limits</li>
            <li>Network issues or infrastructure failures</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            We are not liable for any damages resulting from service interruptions or failed
            automations.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            6. Rate Limits and Usage
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            To ensure fair usage and system stability:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>We may impose rate limits on automation execution</li>
            <li>Excessive usage may result in throttling or temporary suspension</li>
            <li>We reserve the right to modify usage limits at any time with reasonable notice</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">7. Data and Privacy</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            Your privacy is important to us. Please review our{' '}
            <Link to="/privacy" className="text-theme-accent hover:underline">
              Privacy Policy
            </Link>{' '}
            for details on how we collect, use, and protect your data.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            By using the Service, you consent to our data practices as described in the Privacy
            Policy.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            8. Intellectual Property
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            AREA and its original content, features, and functionality are owned by the AREA team
            and are protected by international copyright, trademark, and other intellectual property
            laws.
          </p>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            You retain ownership of your automation configurations and data. By using the Service,
            you grant us a limited license to use your data solely to provide the Service to you.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            9. Limitation of Liability
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            To the maximum extent permitted by law:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>
              AREA is provided &quot;as is&quot; without warranties of any kind, express or implied
            </li>
            <li>We are not liable for any indirect, incidental, or consequential damages</li>
            <li>
              We are not responsible for data loss, failed automations, or issues caused by
              third-party services
            </li>
            <li>
              Our total liability shall not exceed the amount you paid for the Service in the past
              12 months
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">
            10. Account Termination
          </h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            You may delete your account at any time through your profile settings. Upon deletion:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>All automations will be permanently disabled</li>
            <li>OAuth tokens will be revoked</li>
            <li>Your data will be deleted in accordance with our Privacy Policy</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            We reserve the right to suspend or terminate accounts that violate these Terms,
            including but not limited to:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Abuse of the Service or violation of usage policies</li>
            <li>Illegal activities or security threats</li>
            <li>Failure to comply with third-party service terms</li>
            <li>Non-payment of fees (if applicable)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">11. Changes to Terms</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            We may modify these Terms at any time. We will notify users of significant changes via:
          </p>
          <ul className="list-disc list-inside text-lg text-theme-secondary leading-relaxed mt-4 space-y-2">
            <li>Email notification to your registered address</li>
            <li>Prominent notice on the website</li>
            <li>In-app notification</li>
          </ul>
          <p className="text-lg text-theme-secondary leading-relaxed mt-4">
            Your continued use of the Service after changes are posted constitutes acceptance of the
            updated Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">12. Governing Law</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            These Terms are governed by and construed in accordance with applicable laws. Any
            disputes arising from these Terms or your use of the Service shall be resolved through
            good-faith negotiations or, if necessary, binding arbitration.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-3xl font-semibold text-theme-primary mb-4">13. Contact Us</h2>
          <p className="text-lg text-theme-secondary leading-relaxed">
            For questions about these Terms, please contact us at:
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

export default Terms;
