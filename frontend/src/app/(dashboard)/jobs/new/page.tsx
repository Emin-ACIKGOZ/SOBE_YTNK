"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import axios from "axios"; // 👈 Import axios for error checking

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useApp } from "@/hooks/use-app";
import { useToast } from "@/hooks/use-toast";
import { createJob, JobCreatePayload } from "@/lib/api";


// 🚨 FIX 1: Align Zod schema enum values with the backend (JobCreatePayload)
const formSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters long."),
  company_name: z.string().min(2, "Company name is required."),
  location: z.string().min(2, "Location is required."),
  seniority_level: z.enum([
    "INTERNSHIP",
    "ENTRY_LEVEL",
    "JUNIOR_LEVEL",
    "MID_LEVEL",
    "SENIOR_LEVEL",
    "DIRECTOR",
    "EXECUTIVE"
  ]),
  employment_type: z.enum([
    "FULL_TIME",
    "PART_TIME",
    "CONTRACT",
    "INTERNSHIP" // Removed TEMPORARY, added INTERNSHIP (from backend enum)
  ]),
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
      // 🚨 FIX 2: Update default values to match the new enum strings
      seniority_level: "JUNIOR_LEVEL",
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
        // Map multiline strings into arrays
        responsibilities: values.responsibilities.split("\n").map((r) => r.trim()).filter(Boolean),
        qualifications: values.qualifications.split("\n").map((q) => q.trim()).filter(Boolean),
        required_skills: values.required_skills.split("\n").map((s) => s.trim()).filter(Boolean),
        salary: values.salary || undefined,
      };

      const response = await createJob(payload);

      if (response.status !== 201) {
        // This throw statement is okay, but we should handle the error response data below
        throw new Error("Failed to create job posting with non-201 status.");
      }

      toast({
        title: "İş İlanı Oluşturuldu",
        description: `"${values.title}" ünvanına sahip iş ilanı başarılı bir şekilde oluşturuldu.`,
      });

      router.push("/jobs");

    } catch (error: unknown) { // Use unknown for safer type checking
      console.error('Error creating job posting:', error);

      let errorMessage = "İş ilanı oluşturulurken bilinmeyen bir hata oluştu. Lütfen tekrar deneyin.";

      if (axios.isAxiosError(error) && error.response) {
        const responseData = error.response.data;

        // 🚨 CRITICAL FIX 3: Check for 422 and format the error object into a string
        if (error.response.status === 422 && responseData.detail) {
          // FastAPI Pydantic validation errors are in responseData.detail
          const errorMessages = responseData.detail.map((err: any) => {
            // Extract the field name (last part of 'loc') and the message
            const field = err.loc ? err.loc[err.loc.length - 1] : 'Alan';
            return `"${field}": ${err.msg}`;
          });
          errorMessage = errorMessages.join('; ');
        }
        // Handle other simple detail messages or Axios errors
        else if (responseData.detail && typeof responseData.detail === 'string') {
          errorMessage = responseData.detail;
        } else if (error.message) {
          errorMessage = error.message;
        }
      }

      // Pass the fully constructed STRING message to the toast
      toast({
        title: "Hata",
        description: errorMessage, // 👈 Now this is guaranteed to be a STRING
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

              {/* Title, Company, Location fields remain the same */}
              {/* ... */}
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
              {/* ... */}

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
                        {/* 🚨 FIX 4: Update SelectItem values to match Zod and Backend */}
                        <SelectItem value="INTERNSHIP">Stajyer</SelectItem>
                        <SelectItem value="ENTRY_LEVEL">Giriş Seviyesi</SelectItem>
                        <SelectItem value="JUNIOR_LEVEL">Junior</SelectItem>
                        <SelectItem value="MID_LEVEL">Orta Seviye</SelectItem>
                        <SelectItem value="SENIOR_LEVEL">Senior</SelectItem>
                        <SelectItem value="DIRECTOR">Direktör</SelectItem>
                        <SelectItem value="EXECUTIVE">Yönetici</SelectItem>
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
                        {/* 🚨 FIX 5: Update SelectItem values to match Zod and Backend */}
                        <SelectItem value="FULL_TIME">Tam Zamanlı</SelectItem>
                        <SelectItem value="PART_TIME">Yarı Zamanlı</SelectItem>
                        <SelectItem value="CONTRACT">Sözleşmeli</SelectItem>
                        <SelectItem value="INTERNSHIP">Staj</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Description, Responsibilities, Qualifications, Skills, Salary fields remain the same */}
              {/* ... */}
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
              {/* ... */}

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
