'use client';

import type { Candidate } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Progress } from '@/components/ui/progress';
import { FileText } from 'lucide-react';

export function CandidateCard({ candidate }: { candidate: Candidate }) {
  const matchPercentage = Math.round(candidate.matchScore * 100);

  return (
    <Accordion
      type="single"
      collapsible
      className="w-full rounded-lg border bg-card shadow-sm"
    >
      <AccordionItem value={candidate.id} className="border-b-0">
        <AccordionTrigger className="w-full p-4 text-left hover:no-underline [&[data-state=open]>svg:last-child]:-rotate-180">
          <div className="flex w-full items-center gap-4">
            <div className="rounded-lg bg-primary/10 p-3">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <p className="font-semibold">{candidate.fileName}</p>
              <p className="text-sm text-muted-foreground">
                Yüklenme zamanı:{' '}
                {formatDistanceToNow(candidate.createdAt, { addSuffix: true })}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex w-32 flex-col items-end">
                <span className="text-right text-sm font-medium">
                  {matchPercentage}% Eşleşme Skoru
                </span>
                <Progress value={matchPercentage} className="mt-1 h-2" />
              </div>
            </div>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4 pb-4">
          <div className="border-t pt-4">
            <h4 className="mb-2 font-semibold">Yapay Zeka Açıklaması</h4>
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">
              {candidate.reasoning}
            </p>
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
