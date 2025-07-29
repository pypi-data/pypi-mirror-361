import { Polyline } from 'leaflet';
import L from '../leaflet';
import { LeafletPathModel, LeafletPathView } from './Path';
import { LineString, MultiLineString } from 'geojson';
export declare class LeafletPolylineModel extends LeafletPathModel {
    defaults(): {
        _view_name: string;
        _model_name: string;
        locations: never[];
        smooth_factor: number;
        no_clip: boolean;
        stroke: boolean;
        color: string;
        weight: number;
        fill: boolean;
        fill_color: null;
        fill_opacity: number;
        dash_array: null;
        line_cap: string;
        line_join: string;
        pointer_events: string;
        _view_module: string;
        _model_module: string;
        opacity: number;
        bottom: boolean;
        options: string[];
        name: string;
        base: boolean;
        popup: import("@jupyter-widgets/base").WidgetModel | null;
        popup_min_width: number;
        popup_max_width: number;
        popup_max_height: number | null;
        pane: string;
        tooltip: import("@jupyter-widgets/base").WidgetModel | null;
        subitems: L.Layer[];
        pm_ignore: boolean;
        snap_ignore: boolean;
    };
}
export declare class LeafletPolylineView extends LeafletPathView {
    obj: Polyline<LineString | MultiLineString>;
    create_obj(): void;
    model_events(): void;
    update_transform(): void;
}
//# sourceMappingURL=Polyline.d.ts.map