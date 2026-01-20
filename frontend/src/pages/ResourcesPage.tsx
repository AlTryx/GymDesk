import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Box, Plus, Dumbbell, Loader2, Palette } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { ResourceCard } from "@/components/ResourceCard";
import { resourcesApi, type Resource } from "@/api/client";

const PRESET_COLORS = [
  "#ef4444", // red
  "#f97316", // orange
  "#eab308", // yellow
  "#22c55e", // green
  "#06b6d4", // cyan
  "#3b82f6", // blue
  "#8b5cf6", // violet
  "#ec4899", // pink
];

export default function ResourcesPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    type: "Room" as "Room" | "Equipment",
    max_bookings: 1,
    color_code: PRESET_COLORS[0],
  });

  const auth = useAuth();
  // Fetch resources scoped to current user (backend enforces ownership)
  const { data: resourcesData, isLoading } = useQuery({
    queryKey: ["resources"],
    queryFn: () => resourcesApi.list(),
    retry: false,
  });

  // Create resource mutation
  const createMutation = useMutation({
    mutationFn: (data: typeof formData) => resourcesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
      toast({
        title: "Ресурсът е създаден",
        description: "Успешно добавихте нов ресурс.",
      });
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: "Грешка",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const resources = resourcesData?.resources || [];
  const rooms = resources.filter((r) => r.type === "Room");
  const equipment = resources.filter((r) => r.type === "Equipment");

  const resetForm = () => {
    setFormData({
      name: "",
      type: "Room",
      max_bookings: 1,
      color_code: PRESET_COLORS[0],
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const getResourcesList = () => {
    switch (activeTab) {
      case "rooms":
        return rooms;
      case "equipment":
        return equipment;
      default:
        return resources;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Ресурси</h1>
          <p className="text-muted-foreground">
            Преглед и управление на фитнес ресурси
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={(open) => { setIsDialogOpen(open); if (!open) resetForm(); }}>
          {auth.role === 'ADMIN' && (
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Добави ресурс
              </Button>
            </DialogTrigger>
          )}
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Добавяне на ресурс</DialogTitle>
              <DialogDescription>
                Създайте нов ресурс за резервации
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Име на ресурса</Label>
                <Input
                  id="name"
                  placeholder="напр. Зала за йога"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="type">Тип</Label>
                <Select
                  value={formData.type}
                  onValueChange={(value: "Room" | "Equipment") =>
                    setFormData({ ...formData, type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Room">
                      <span className="flex items-center gap-2">
                        <Box className="h-4 w-4" />
                        Зала
                      </span>
                    </SelectItem>
                    <SelectItem value="Equipment">
                      <span className="flex items-center gap-2">
                        <Dumbbell className="h-4 w-4" />
                        Уред
                      </span>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_bookings">Максимален брой резервации</Label>
                <Input
                  id="max_bookings"
                  type="number"
                  min={1}
                  max={50}
                  value={formData.max_bookings}
                  onChange={(e) =>
                    setFormData({ ...formData, max_bookings: parseInt(e.target.value) || 1 })
                  }
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Колко едновременни резервации са разрешени
                </p>
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Palette className="h-4 w-4" />
                  Цвят
                </Label>
                <div className="flex flex-wrap gap-2">
                  {PRESET_COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      className={`h-8 w-8 rounded-full border-2 transition-transform hover:scale-110 ${formData.color_code === color
                        ? "border-foreground scale-110"
                        : "border-transparent"
                        }`}
                      style={{ backgroundColor: color }}
                      onClick={() => setFormData({ ...formData, color_code: color })}
                    />
                  ))}
                </div>
              </div>

              <DialogFooter>
                <Button type="submit" disabled={createMutation.isPending} className="w-full gap-2">
                  {createMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Създаване...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      Създай ресурс
                    </>
                  )}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-foreground">{resources.length}</div>
              <div className="text-sm text-muted-foreground">Общо ресурси</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-foreground">{rooms.length}</div>
              <div className="text-sm text-muted-foreground">Зали</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-foreground">{equipment.length}</div>
              <div className="text-sm text-muted-foreground">Уреди</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">Всички ({resources.length})</TabsTrigger>
          <TabsTrigger value="rooms" className="gap-2">
            <Box className="h-4 w-4" />
            Зали ({rooms.length})
          </TabsTrigger>
          <TabsTrigger value="equipment" className="gap-2">
            <Dumbbell className="h-4 w-4" />
            Уреди ({equipment.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-6">
          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-40 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : getResourcesList().length === 0 ? (
            <Card className="p-12 text-center">
              <Box className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-lg font-medium mb-2">Няма ресурси</h3>
              <p className="text-muted-foreground mb-4">
                {activeTab === "all"
                  ? "Добавете първия си ресурс"
                  : activeTab === "rooms"
                    ? "Няма добавени зали"
                    : "Няма добавени уреди"}
              </p>
              {auth.role === 'ADMIN' && (
                <Button onClick={() => setIsDialogOpen(true)} className="gap-2">
                  <Plus className="h-4 w-4" />
                  Добави ресурс
                </Button>
              )}
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {getResourcesList().map((resource) => (
                <ResourceCard key={resource.id} resource={resource} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
