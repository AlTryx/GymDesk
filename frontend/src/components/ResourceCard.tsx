import { Box, Users, Dumbbell, Calendar } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Resource } from "@/api/client";

interface ResourceCardProps {
  resource: Resource;
  onSelect?: (resource: Resource) => void;
  isSelected?: boolean;
}

export function ResourceCard({ resource, onSelect, isSelected }: ResourceCardProps) {
  const isRoom = resource.type === "Room";

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
          <Button
            className="w-full gap-2 mt-2"
            style={{
              backgroundColor: resource.color_code,
              color: "#fff",
            }}
          >
            <Calendar className="h-4 w-4" />
            Резервирай
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
