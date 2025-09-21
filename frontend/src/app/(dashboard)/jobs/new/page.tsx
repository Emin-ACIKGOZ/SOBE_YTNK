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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useApp } from "@/hooks/use-app";
import { useToast } from "@/hooks/use-toast";
import { createJob, JobCreatePayload } from "@/lib/api";


const formSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters long."),
  company_name: z.string().min(2, "Company name is required."),
  location: z.string().min(2, "Location is required."),
  seniority_level: z.enum(["INTERNSHIP", "JUNIOR", "MID", "SENIOR", "LEAD"]),
  employment_type: z.enum(["FULL_TIME", "PART_TIME", "CONTRACT", "TEMPORARY"]),
  description: z.string().min(20, "Description must be at least 20 characters long."),
  responsibilities: z.string().min(5, "Responsibilities are required."),
  qualifications: z.string().min(5, "Qualifications are required."),
  required_skills: z.string().min(5, "Required skills are required."),
  salary: z.string().optional(),
});

export default function NewJobPage() {
  const router = useRouter();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      company_name: "",
      location: "",
      seniority_level: "INTERNSHIP",
      employment_type: "FULL_TIME",
      description: "",
      responsibilities: "",
      qualifications: "",
      required_skills: "",
      salary: "",
    },
  });
  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const payload: JobCreatePayload = {
        title: values.title,
        company_name: values.company_name,
        location: values.location,
        seniority_level: values.seniority_level,
        employment_type: values.employment_type,
        description: values.description,
        responsibilities: values.responsibilities.split("\n").map((r) => r.trim()).filter(Boolean),
        qualifications: values.qualifications.split("\n").map((q) => q.trim()).filter(Boolean),
        required_skills: values.required_skills.split("\n").map((s) => s.trim()).filter(Boolean),
        salary: values.salary || undefined,
      };

      const response = await createJob(payload);

      if (response.status !== 201) {
        throw new Error("Failed to create job posting");
      }

      toast({
        title: "İş İlanı Oluşturuldu",
        description: `"${values.title}" ünvanına sahip iş ilanı başarılı bir şekilde oluşturuldu.`,
      });

      router.push("/jobs");
    } catch (error: any) {
      console.error('Error creating job posting:', error);
      const errorMessage = error.response?.data?.detail ||
        error.message ||
        "İş ilanı oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.";
      toast({
        title: "Hata",
        description: errorMessage,
        variant: "destructive",
      });
    }
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
                name="company_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Şirket Adı</FormLabel>
                    <FormControl>
                      <Input placeholder="Şirket adı" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="location"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Konum</FormLabel>
                    <FormControl>
                      <Input placeholder="Şehir, Ülke" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="seniority_level"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tecrübe Seviyesi</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seçiniz" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="INTERNSHIP">Stajyer</SelectItem>
                        <SelectItem value="JUNIOR">Junior</SelectItem>
                        <SelectItem value="MID">Orta</SelectItem>
                        <SelectItem value="SENIOR">Senior</SelectItem>
                        <SelectItem value="LEAD">Lead</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="employment_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Çalışma Türü</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seçiniz" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="FULL_TIME">Tam Zamanlı</SelectItem>
                        <SelectItem value="PART_TIME">Yarı Zamanlı</SelectItem>
                        <SelectItem value="CONTRACT">Sözleşmeli</SelectItem>
                        <SelectItem value="TEMPORARY">Geçici</SelectItem>
                      </SelectContent>
                    </Select>
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
                name="responsibilities"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sorumluluklar</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Her satıra bir sorumluluk yazın&#10;örn:&#10;- Yazılım geliştirme&#10;- Kod inceleme&#10;- Takım çalışması"
                        rows={4}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="qualifications"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gereklilikler / Nitelikler</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Her satıra bir gereklilik yazın&#10;örn:&#10;- Bilgisayar mühendisliği mezunu&#10;- 3+ yıl deneyim&#10;- İngilizce bilgisi"
                        rows={4}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="required_skills"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gerekli Beceriler</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Her satıra bir beceri yazın&#10;örn:&#10;- JavaScript&#10;- React&#10;- Node.js"
                        rows={4}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="salary"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Maaş (İsteğe Bağlı)</FormLabel>
                    <FormControl>
                      <Input placeholder="örn; 15.000 TL / ay veya 180.000 TL / yıl" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => router.back()}>
                  İptal
                </Button>
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