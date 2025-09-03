"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useApp } from "@/hooks/use-app";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters long."),
  description: z.string().min(20, "Description must be at least 20 characters long."),
  requirements: z.string().min(20, "Requirements must be at least 20 characters long."),
});

export default function NewJobPage() {
  const router = useRouter();
  const { addJobPosting } = useApp();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      description: "",
      requirements: "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    addJobPosting(values);
    toast({
      title: "İş İlanı Oluşturdu",
      description: `"${values.title} ünvanına sahip iş ilanı başarılı bir şekilde oluşturuldu." `,
    });
    router.push("/jobs");
  }

  return (
    <div className="container mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">Yeni İş İlanı Oluştur</CardTitle>
          <CardDescription>Yeni bir açık pozisyon oluşturmak için aşağıdaki bilgileri doldurun.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>İş Ünvanı</FormLabel>
                    <FormControl>
                      <Input placeholder="örn; Kıdemli Yazılım Mühendisi" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>İş Açıklaması</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Rolü ve sorumlulukları tanımlayın." rows={6} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="requirements"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gereksinimler</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Gerekli becerileri ve deneyimi listeleyin." rows={6} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
                <Button type="submit" disabled={form.formState.isSubmitting}>
                  İlan Oluştur
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
