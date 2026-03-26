import { NextResponse } from 'next/navigation';
import crypto from 'crypto';
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

// Verify the payload came from GitHub using the secret
function verifySignature(req: Request, payload: string, signature: string | null) {
  const secret = process.env.GITHUB_WEBHOOK_SECRET;
  if (!secret) {
    console.warn('GITHUB_WEBHOOK_SECRET is not set. Skipping signature verification.');
    return true; // If you haven't set the secret yet, allow it to pass for testing
  }
  
  if (!signature) return false;

  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  
  return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(signature));
}

export async function POST(req: Request) {
  try {
    const rawBody = await req.text();
    const signature = req.headers.get('x-hub-signature-256');
    const event = req.headers.get('x-github-event');

    // Verify the webhook is actually from GitHub
    if (!verifySignature(req, rawBody, signature)) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const payload = JSON.parse(rawBody);

    // We only care about 'star' events right now
    if (event === 'star' && payload.action === 'created') {
      const starrer = payload.sender.login;
      const starrerUrl = payload.sender.html_url;
      const repoName = payload.repository.full_name;
      const totalStars = payload.repository.stargazers_count;

      // Send the Lead Intelligence Email
      await resend.emails.send({
        from: 'Aethelgard Intelligence <admin@securepasspro.co>',
        to: ['admin@securepasspro.co'],
        subject: `🚨 LEAD ALERT: New GitHub Star on ${repoName}`,
        html: `
          <div style="font-family: monospace; background-color: #0a0a0a; color: #10b981; padding: 30px; border-radius: 10px;">
            <h2 style="color: #fff; text-transform: uppercase; border-bottom: 1px solid #333; padding-bottom: 10px;">
              Aethelgard Lead Intelligence
            </h2>
            <p><strong>Event:</strong> New Repository Star</p>
            <p><strong>Target:</strong> ${repoName}</p>
            <p><strong>Total Stars:</strong> ${totalStars}</p>
            <br/>
            <h3 style="color: #fff;">Actor Profile:</h3>
            <p><strong>Username:</strong> ${starrer}</p>
            <p><strong>GitHub Profile:</strong> <a href="${starrerUrl}" style="color: #3b82f6;">${starrerUrl}</a></p>
            <br/>
            <div style="background-color: #111; padding: 15px; border-left: 4px solid #3b82f6;">
              <p style="margin: 0; color: #94a3b8;"><strong>Next Action:</strong></p>
              <p style="margin: 5px 0 0 0; color: #fff;">Cross-reference this username on LinkedIn. If they are a Security Architect, CISO, or DevSecOps Engineer, initiate outreach immediately.</p>
            </div>
          </div>
        `
      });

      console.log(`[LEAD INTEL] Notification sent for star by ${starrer}`);
    }

    // Always return 200 OK to GitHub so they know we received it
    return NextResponse.json({ received: true }, { status: 200 });

  } catch (error) {
    console.error('Webhook processing error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
