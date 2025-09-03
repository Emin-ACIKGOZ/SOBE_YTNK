"use client";

import type { Candidate } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Progress } from "@/components/ui/progress";
import { FileText } from "lucide-react";

export function CandidateCard({ candidate }: { candidate: Candidate }) {
  const matchPercentage = Math.round(candidate.matchScore * 100);

  return (
  <Accordion type="single" collapsible className="w-full bg-card rounded-lg border shadow-sm">
    <AccordionItem value={candidate.id} className="border-b-0">
    <AccordionTrigger className="w-full hover:no-underline p-4 text-left [&[data-state=open]>svg:last-child]:-rotate-180">
      <div className="flex items-center gap-4 w-full">
        <div className="p-3 rounded-lg bg-primary/10">
          <FileText className="h-6 w-6 text-primary" />
        </div>
        <div className="flex-1">
          <p className="font-semibold">{candidate.fileName}</p>
          <p className="text-sm text-muted-foreground">
            Yüklenme zamanı: {formatDistanceToNow(candidate.createdAt, { addSuffix: true })}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end w-32">
            <span className="text-sm font-medium text-right">{matchPercentage}% Eşleşme Skoru</span>
            <Progress value={matchPercentage} className="h-2 mt-1" />
          </div>
        </div>
      </div>
    </AccordionTrigger>
    <AccordionContent className="px-4 pb-4">
      <div className="pt-4 border-t">
        <h4 className="font-semibold mb-2">Yapay Zeka Açıklaması</h4>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">{candidate.reasoning}</p>
      </div>
    </AccordionContent>
    </AccordionItem>
  </Accordion>
  );
}
