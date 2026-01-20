import { Box, Users, Dumbbell, Calendar, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Resource } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { timeslotsApi } from "@/api/client";
import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface ResourceCardProps {
  resource: Resource;
  onSelect?: (resource: Resource) => void;
  isSelected?: boolean;
}

export function ResourceCard({ resource, onSelect, isSelected }: ResourceCardProps) {
  const isRoom = resource.type === "Room";
  const auth = useAuth();
  const { toast: showToast } = useToast();

  const handleGenerate = async (e: any) => {
    // prevent card-level click from firing
    e.stopPropagation();
    if (!confirm(`Генерирам часове за "${resource.name}" за следващите 30 дни?`)) return;
    try {
      const start = new Date();
      const end = new Date();
      end.setDate(end.getDate() + 30);
      await timeslotsApi.generate({
        resource_id: resource.id,
        start_date: start.toISOString(),
        end_date: end.toISOString(),
        duration_minutes: 60,
      });
      showToast({ title: 'Готово', description: 'Часовете бяха генерирани', variant: 'default' });
    } catch (err: any) {
      showToast({ title: 'Грешка', description: err?.message || 'Неуспешно генериране', variant: 'destructive' });
    }
  };

  // Dialog state for manual generation (admin only)
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [startDate, setStartDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [endDate, setEndDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 30);
    return d.toISOString().slice(0, 10);
  });
  const [duration, setDuration] = useState<number>(60);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const queryClient = useQueryClient();

  const handleDialogSubmit = async (e: React.FormEvent) => {
    e.stopPropagation();
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const startIso = new Date(startDate).toISOString();
      const endIso = new Date(endDate).toISOString();
      await timeslotsApi.generate({
        resource_id: resource.id,
        start_date: startIso,
        end_date: endIso,
        duration_minutes: duration,
      });
      showToast({ title: 'Готово', description: 'Часовете бяха генерирани', variant: 'default' });
      setIsDialogOpen(false);
      // Refresh timeslots and reservations after generation
      queryClient.invalidateQueries({ queryKey: ["timeslots"] });
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
    } catch (err: any) {
      showToast({ title: 'Грешка', description: err?.message || 'Неуспешно генериране', variant: 'destructive' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card
      className={cn(
        "group relative cursor-pointer overflow-hidden transition-all duration-300 hover:shadow-lg",
        isSelected && "ring-2 ring-primary ring-offset-2"
      )}
      onClick={() => onSelect?.(resource)}
    >
      {/* Color accent bar */}
      <div
        className="absolute top-0 left-0 right-0 h-1"
        style={{ backgroundColor: resource.color_code }}
      />

      <CardHeader className="pt-6 pb-3">
        <div className="flex items-start justify-between gap-2">
          <div
            className="flex h-12 w-12 items-center justify-center rounded-xl transition-transform group-hover:scale-105"
            style={{ backgroundColor: `${resource.color_code}20` }}
          >
            {isRoom ? (
              <Box className="h-6 w-6" style={{ color: resource.color_code }} />
            ) : (
              <Dumbbell className="h-6 w-6" style={{ color: resource.color_code }} />
            )}
          </div>
          <Badge variant="outline">{isRoom ? "Зала" : "Уред"}</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <div>
          <h3 className="font-semibold text-lg text-card-foreground">{resource.name}</h3>
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Users className="h-4 w-4" />
            <span>Макс. {resource.max_bookings} резервации</span>
          </div>
        </div>

        {onSelect && (
          <div className="mt-2 flex gap-2">
            {auth.role === 'ADMIN' && (
              <>
                <Dialog open={isDialogOpen} onOpenChange={(open) => setIsDialogOpen(open)}>
                  <DialogTrigger asChild>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => { e.stopPropagation(); setIsDialogOpen(true); }}
                    >
                      Генерирай часове
                    </Button>
                  </DialogTrigger>
                  <DialogContent onClick={(e) => e.stopPropagation()}>
                    <DialogHeader>
                      <DialogTitle>Генериране на слотове</DialogTitle>
                      <DialogDescription>Изберете период и продължителност за генериране на часови слотове.</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleDialogSubmit} className="space-y-4 py-2">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor={`start-${resource.id}`}>Начална дата</Label>
                          <Input id={`start-${resource.id}`} type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
                        </div>
                        <div>
                          <Label htmlFor={`end-${resource.id}`}>Крайна дата</Label>
                          <Input id={`end-${resource.id}`} type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor={`duration-${resource.id}`}>Продължителност (минути)</Label>
                        <select id={`duration-${resource.id}`} value={duration} onChange={(e) => setDuration(parseInt(e.target.value))} className="w-full rounded-md border px-3 py-2">
                          {[15, 30, 45, 60, 90, 120].map((d) => (
                            <option key={d} value={d}>{d} мин</option>
                          ))}
                        </select>
                      </div>

                      <DialogFooter>
                        <Button type="submit" disabled={isSubmitting} className="gap-2">
                          {isSubmitting ? (<><Loader2 className="h-4 w-4 animate-spin" /> Генериране...</>) : ("Генерирай")}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </>
            )}
            <Button
              className="flex-1 gap-2"
              style={{
                backgroundColor: resource.color_code,
                color: "#fff",
              }}
            >
              <Calendar className="h-4 w-4" />
              Резервирай
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
