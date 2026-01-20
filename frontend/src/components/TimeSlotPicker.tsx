import { Clock, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { TimeSlot } from "@/api/client";
import { format } from "date-fns";
import { bg } from "date-fns/locale";

interface TimeSlotPickerProps {
  timeSlots: TimeSlot[];
  selectedSlot: TimeSlot | null;
  onSelect: (slot: TimeSlot) => void;
  isLoading?: boolean;
}

export function TimeSlotPicker({
  timeSlots,
  selectedSlot,
  onSelect,
  isLoading = false,
}: TimeSlotPickerProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="h-12 rounded-lg bg-muted animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (timeSlots.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Clock className="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p>Няма налични часове за избраната дата</p>
      </div>
    );
  }

  // Group slots by date
  const slotsByDate = timeSlots.reduce((acc, slot) => {
    const date = format(new Date(slot.start_time), "yyyy-MM-dd");
    if (!acc[date]) acc[date] = [];
    acc[date].push(slot);
    return acc;
  }, {} as Record<string, TimeSlot[]>);

  return (
    <div className="space-y-6">
      {Object.entries(slotsByDate).map(([date, slots]) => (
        <div key={date}>
          <h4 className="text-sm font-medium text-muted-foreground mb-3">
            {format(new Date(date), "EEEE, d MMMM", { locale: bg })}
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
            {slots.map((slot) => {
              const isSelected = selectedSlot?.id === slot.id;
              const startTime = new Date(slot.start_time);
              const endTime = new Date(slot.end_time);

              return (
                <Button
                  key={slot.id}
                  variant={isSelected ? "default" : "outline"}
                  className={cn(
                    "h-auto py-3 flex-col gap-0.5 transition-all",
                    !slot.is_available && "opacity-50 cursor-not-allowed",
                    isSelected && "ring-2 ring-primary ring-offset-2"
                  )}
                  disabled={!slot.is_available}
                  onClick={() => onSelect(slot)}
                >
                  <span className="font-semibold">
                    {format(startTime, "HH:mm")}
                  </span>
                  <span className="text-xs opacity-70">
                    до {format(endTime, "HH:mm")}
                  </span>
                  {isSelected && (
                    <Check className="h-4 w-4 mt-1" />
                  )}
                </Button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
