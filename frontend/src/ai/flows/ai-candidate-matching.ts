'use server';

/**
 * @fileOverview Matches uploaded CVs to İş İlanları using AI.
 *
 * - matchCandidate - A function that takes a İş İlanları description and a CV data URI, and returns a score indicating how well the candidate matches the job.
 * - MatchCandidateInput - The input type for the matchCandidate function.
 * - MatchCandidateOutput - The return type for the matchCandidate function.
 */

import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const MatchCandidateInputSchema = z.object({
  jobDescription: z.string().describe('The description of the İş İlanları.'),
  cvDataUri: z.string().describe(
    "The CV of the candidate, as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'.", // using single quotes to avoid escaping
  ),
});
export type MatchCandidateInput = z.infer<typeof MatchCandidateInputSchema>;

const MatchCandidateOutputSchema = z.object({
  matchScore: z
    .number()
    .describe(
      'A score between 0 and 1 indicating how well the candidate matches the İş İlanları. Higher scores indicate a better match.',
    ),
  reasoning: z
    .string()
    .describe(
      'Explanation of why the model assessed the match score, pointing out specific strengths and weaknesses of the candidate relative to the job description.',
    ),
});
export type MatchCandidateOutput = z.infer<typeof MatchCandidateOutputSchema>;

export async function matchCandidate(
  input: MatchCandidateInput,
): Promise<MatchCandidateOutput> {
  return matchCandidateFlow(input);
}

const prompt = ai.definePrompt({
  name: 'matchCandidatePrompt',
  input: { schema: MatchCandidateInputSchema },
  output: { schema: MatchCandidateOutputSchema },
  prompt: `You are an expert HR assistant whose job is to score candidates fit for the job they applied for.

You will be provided a job description and the text content of the candidate's CV.

Based on these two inputs, you will:
1. Determine a match score (between 0 and 1) indicating how well the candidate matches the İş İlanları.
2. Provide reasoning for the match score, pointing out specific strengths and weaknesses of the candidate relative to the job description.

Job Description: {{{jobDescription}}}

CV Text: {{media url=cvDataUri}}

Ensure that the matchScore is a number between 0 and 1, and that the reasoning clearly explains the rationale behind the score.`, // Added instructions to ensure matchScore is between 0 and 1
});

const matchCandidateFlow = ai.defineFlow(
  {
    name: 'matchCandidateFlow',
    inputSchema: MatchCandidateInputSchema,
    outputSchema: MatchCandidateOutputSchema,
  },
  async (input) => {
    const { output } = await prompt(input);
    return output!;
  },
);
