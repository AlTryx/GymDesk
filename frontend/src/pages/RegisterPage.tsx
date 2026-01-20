import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Dumbbell, Mail, User, Lock, ArrowRight, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
    const navigate = useNavigate();
    const { toast } = useToast();
    const auth = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        email: "",
        username: "",
        password: "",
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            await auth.register(formData.email, formData.username, formData.password);
            setIsLoading(false);
            toast({ title: "Регистрация успешна", description: "Добре дошли в GymDesk!" });
            navigate('/');
        } catch (err: any) {
            setIsLoading(false);
            toast({ title: "Грешка при регистрация", description: err?.message || 'Неуспешна регистрация', variant: 'destructive' });
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
            <div className="w-full max-w-md space-y-8">
                <div className="text-center">
                    <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-primary mb-4">
                        <Dumbbell className="h-8 w-8 text-primary-foreground" />
                    </div>
                    <h1 className="text-3xl font-bold text-foreground">GymDesk</h1>
                    <p className="text-muted-foreground mt-2">Създайте ваш акаунт</p>
                </div>

                <Card className="border-border/50 shadow-lg">
                    <CardHeader className="space-y-1 pb-4">
                        <CardTitle className="text-2xl text-center">Регистрация</CardTitle>
                        <CardDescription className="text-center">Създайте нов акаунт</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Имейл адрес</Label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input id="email" type="email" placeholder="ivan@example.com" className="pl-10" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="username">Потребителско име</Label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input id="username" placeholder="ivan123" className="pl-10" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} required />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">Парола</Label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input id="password" type="password" placeholder="••••••••" className="pl-10" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} required />
                                </div>
                            </div>

                            <Button type="submit" className="w-full gap-2" disabled={isLoading}>
                                {isLoading ? (
                                    <>
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        Регистрация...
                                    </>
                                ) : (
                                    <>
                                        Регистрация
                                        <ArrowRight className="h-4 w-4" />
                                    </>
                                )}
                            </Button>
                        </form>
                        <div className="mt-6 text-center text-sm text-muted-foreground">
                            <p>Вече имате акаунт? <Link to="/login" className="text-primary underline">Вход</Link></p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
