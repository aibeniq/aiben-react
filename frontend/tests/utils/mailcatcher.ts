import type { APIRequestContext } from "@playwright/test"

type Email = {
  id: number
  recipients: string[]
  subject: string
}

async function findEmail({
  request,
  filter,
}: {
  request: APIRequestContext
  filter?: (email: Email) => boolean
}) {
  if (!process.env.MAILCATCHER_HOST) {
    throw new Error("MAILCATCHER_HOST environment variable is not set!")
  }

  try {
    const response = await request.get(`${process.env.MAILCATCHER_HOST}/messages`)

    if (!response.ok()) {
      throw new Error(`Failed to fetch emails: ${response.status()} - ${response.statusText()}`)
    }

    let emails: Email[] = await response.json()

    if (filter) {
      emails = emails.filter(filter)
    }

    const email = emails[emails.length - 1]

    if (email) {
      return email as Email
    }

    return null
  } catch (error) {
    console.error(`Network error when fetching emails:`, error)
    return null
  }
}

export function findLastEmail({
  request,
  filter,
  timeout = 5000,
}: {
  request: APIRequestContext
  filter?: (email: Email) => boolean
  timeout?: number
}) {
  const timeoutPromise = new Promise<never>((_, reject) =>
    setTimeout(() => {
      reject(new Error("Timeout while trying to get latest email"))
    }, timeout),
  )

  const checkEmails = async () => {
    while (true) {
      const emailData = await findEmail({ request, filter })

      if (emailData) {
        return emailData
      }

      // Wait for 100ms before checking again
      await new Promise((resolve) => setTimeout(resolve, 100))
    }
  }

  return Promise.race([timeoutPromise, checkEmails()])
}
