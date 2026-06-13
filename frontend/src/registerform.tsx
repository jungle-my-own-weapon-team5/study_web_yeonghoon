"use client";

import * as React from "react";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { toast, Toaster } from "sonner";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupText,
  InputGroupTextarea,
} from "@/components/ui/input-group";
import { Eye, EyeOff } from "lucide-react";

type RegisterProps = {
  registerPage: boolean;
  setRegisterPage: React.Dispatch<React.SetStateAction<boolean>>;
};

type RegisterDataType = {
  id: string;
  Description: string;
  characters: number;
  regist_id: RegisterFieldName;
};

type RegisterFieldName =
  | "user_id"
  | "nick_name"
  | "email"
  | "password"
  | "name"
  | "birthday";

const registerData: RegisterDataType[] = [
  {
    id: "id",
    Description: "아이디 / kimjanghoon",
    characters: 32,
    regist_id: "user_id",
  },
  {
    id: "nick_name",
    Description: "닉네임 / supteunjhun",
    characters: 32,
    regist_id: "nick_name",
  },
  {
    id: "email",
    Description: "이메일 / supteunjhun@naver.com",
    characters: 48,
    regist_id: "email",
  },
  {
    id: "password",
    Description: "패스워드 / 1234",
    characters: 32,
    regist_id: "password",
  },
  {
    id: "name",
    Description: "실제 이름 / ex)김장훈",
    characters: 32,
    regist_id: "name",
  },
  {
    id: "birthday",
    Description: "생년월일 / ex)20260613",
    characters: 8,
    regist_id: "birthday",
  },
];

const formSchema = z.object({
  user_id: z.string().nonempty().max(32, "id must be most 32 characters"),
  nick_name: z
    .string()
    .nonempty()
    .max(32, "nick_name must be most 32 characters"),
  email: z.string().nonempty().max(48, "email must be most 48 characters"),
  password: z
    .string()
    .nonempty()
    .min(8, "password must be more than 32 characters")
    .max(32, "password must be most 32 characters"),
  name: z.string().nonempty().max(32, "name must be most 32 characters"),
  birthday: z.string().nonempty().length(8, "birthday must be 8 characters"),
});

export function RegisterForm({ registerPage, setRegisterPage }: RegisterProps) {
  const [showPassword, setShowPassword] = useState<boolean>(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      user_id: "",
      nick_name: "",
      email: "",
      password: "",
      name: "",
      birthday: "",
    },
  });

  async function onSubmit(data: z.infer<typeof formSchema>): Promise<void> {
    const body = {
      ...data,
    };
    const res = await fetch("http://localhost:8000/register", {
      method: "post",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const message_data = await res.json();
    console.log(message_data)
    if (res.ok) {
    toast(message_data.message, {
      description: (
        <pre className="mt-2 w-[320px] overflow-x-auto rounded-md bg-code p-4 text-code-foreground">
          <code>
            {`id : ${data.user_id}\n`}
            {`nick_name : ${data.nick_name}\n`}
            {`email : ${data.email}\n`}
            {`password : ${data.password}\n`}
            {`name : ${data.name}\n`}
            {`birthday : ${data.birthday}\n`}
          </code>
        </pre>
      ),
      position: "bottom-right",
      classNames: {
        content: "flex flex-col gap-2",
      },
      style: {
        "--border-radius": "calc(var(--radius)  + 4px)",
      } as React.CSSProperties,
    });
    setRegisterPage((prev)=>!prev)
  }
   else {
    toast(message_data.detail, {
      description: (
        <pre className="mt-2 w-[320px] overflow-x-auto rounded-md bg-code p-4 text-code-foreground">
          <code>
            {`${data.user_id}가 이미 존재합니다.`}
          </code>
        </pre>
      ),
      position: "bottom-right",
      classNames: {
        content: "flex flex-col gap-2",
      },
      style: {
        "--border-radius": "calc(var(--radius)  + 4px)",
      } as React.CSSProperties,
    });
  }
  }

  return (
    <Card className="w-full sm:max-w-2xl">
      <CardHeader>
        <CardTitle>Register Form</CardTitle>
        <CardDescription>Regist your account</CardDescription>
      </CardHeader>
      <CardContent>
        <form id="form-rhf-demo" onSubmit={form.handleSubmit(onSubmit)}>
          <FieldGroup>
            {registerData.map((menu) => (
              <Controller
                name={menu.regist_id}
                control={form.control}
                key={menu.Description}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-rhf-demo-description">
                      {menu.id}
                    </FieldLabel>
                    <InputGroup>
                      <Input
                        {...field}
                        id="form-rhf-demo-description"
                        placeholder={`${menu.Description} / ${menu.characters} characters`}
                        type={
                          menu.id === "password" && !showPassword
                            ? "password"
                            : "text"
                        }
                        className="min-h-7 resize-none"
                        aria-invalid={fieldState.invalid}
                      />
                      {menu.id === "password" ? (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-1 top-1/2 -translate-y-1/2"
                          onClick={() => setShowPassword((prev) => !prev)}
                        >
                          {showPassword ? <EyeOff /> : <Eye />}
                        </Button>
                      ) : (
                        <></>
                      )}
                    </InputGroup>
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
            ))}
          </FieldGroup>
        </form>
      </CardContent>
      <CardFooter>
        <Field orientation="horizontal">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setRegisterPage(!registerPage);
            }}
          >
            Cancel
          </Button>
          <Button type="button" variant="outline" onClick={() => form.reset()}>
            Reset
          </Button>
          <Button type="submit" form="form-rhf-demo">
            Submit
          </Button>
        </Field>
      </CardFooter>
    </Card>
  );
}
