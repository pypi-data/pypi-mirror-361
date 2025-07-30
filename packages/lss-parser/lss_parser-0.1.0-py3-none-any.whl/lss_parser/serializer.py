"""
Serializer for converting Run objects back to XML.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

from .models import Attempt, AutoSplitterSettings, Metadata, Run, Segment, Time


class LSSSerializer:
    """Serializer for converting Run objects back to XML."""
    
    @staticmethod
    def _create_time_element(parent: ET.Element, time: Time) -> None:
        """Create time subelements for a parent element."""
        if time.real_time is not None:
            real_time_elem = ET.SubElement(parent, 'RealTime')
            real_time_elem.text = time.real_time
            
        if time.game_time is not None:
            game_time_elem = ET.SubElement(parent, 'GameTime')
            game_time_elem.text = time.game_time
            
        if time.pause_time is not None:
            pause_time_elem = ET.SubElement(parent, 'PauseTime')
            pause_time_elem.text = time.pause_time
    
    @staticmethod
    def _create_metadata_element(parent: ET.Element, metadata: Metadata) -> None:
        """Create metadata element."""
        metadata_elem = ET.SubElement(parent, 'Metadata')
        
        run_elem = ET.SubElement(metadata_elem, 'Run')
        run_elem.set('id', metadata.run_id)
        
        platform_elem = ET.SubElement(metadata_elem, 'Platform')
        platform_elem.set('usesEmulator', str(metadata.platform_uses_emulator))
        platform_elem.text = metadata.platform
        
        region_elem = ET.SubElement(metadata_elem, 'Region')
        region_elem.text = metadata.region
        
        variables_elem = ET.SubElement(metadata_elem, 'Variables')
        for key, value in metadata.variables.items():
            var_elem = ET.SubElement(variables_elem, key)
            var_elem.text = value
            
        if metadata.custom_variables:
            custom_variables_elem = ET.SubElement(metadata_elem, 'CustomVariables')
            for key, value in metadata.custom_variables.items():
                var_elem = ET.SubElement(custom_variables_elem, key)
                var_elem.text = value
    
    @staticmethod
    def _create_attempt_element(parent: ET.Element, attempt: Attempt) -> None:
        """Create attempt element."""
        attempt_elem = ET.SubElement(parent, 'Attempt')
        attempt_elem.set('id', attempt.id)
        
        if attempt.started:
            attempt_elem.set('started', attempt.started)
        attempt_elem.set('isStartedSynced', str(attempt.is_started_synced))
        
        if attempt.ended:
            attempt_elem.set('ended', attempt.ended)
        attempt_elem.set('isEndedSynced', str(attempt.is_ended_synced))
        
        LSSSerializer._create_time_element(attempt_elem, attempt.time)
    
    @staticmethod
    def _create_segment_element(parent: ET.Element, segment: Segment) -> None:
        """Create segment element."""
        segment_elem = ET.SubElement(parent, 'Segment')
        
        name_elem = ET.SubElement(segment_elem, 'Name')
        name_elem.text = segment.name
        
        icon_elem = ET.SubElement(segment_elem, 'Icon')
        icon_elem.text = segment.icon
        
        # Split times
        split_times_elem = ET.SubElement(segment_elem, 'SplitTimes')
        for split_time in segment.split_times:
            split_time_elem = ET.SubElement(split_times_elem, 'SplitTime')
            split_time_elem.set('name', split_time.name)
            LSSSerializer._create_time_element(split_time_elem, split_time.time)
        
        # Best segment time
        best_segment_elem = ET.SubElement(segment_elem, 'BestSegmentTime')
        LSSSerializer._create_time_element(best_segment_elem, segment.best_segment_time)
        
        # Segment history
        segment_history_elem = ET.SubElement(segment_elem, 'SegmentHistory')
        for segment_time in segment.segment_history:
            time_elem = ET.SubElement(segment_history_elem, 'Time')
            time_elem.set('id', segment_time.id)
            LSSSerializer._create_time_element(time_elem, segment_time.time)
    
    @staticmethod
    def _create_auto_splitter_settings_element(parent: ET.Element, settings: AutoSplitterSettings) -> None:
        """Create auto splitter settings element."""
        settings_elem = ET.SubElement(parent, 'AutoSplitterSettings')
        
        auto_reset_elem = ET.SubElement(settings_elem, 'AutoReset')
        auto_reset_elem.text = str(settings.auto_reset)
        
        set_high_priority_elem = ET.SubElement(settings_elem, 'SetHighPriority')
        set_high_priority_elem.text = str(settings.set_high_priority)
        
        set_game_time_elem = ET.SubElement(settings_elem, 'SetGameTime')
        set_game_time_elem.text = str(settings.set_game_time)
        
        file_time_offset_elem = ET.SubElement(settings_elem, 'FileTimeOffset')
        file_time_offset_elem.text = str(settings.file_time_offset)
        
        if settings.splits:
            splits_elem = ET.SubElement(settings_elem, 'Splits')
            for split in settings.splits:
                split_elem = ET.SubElement(splits_elem, 'Split')
                split_elem.text = split
    
    @staticmethod
    def serialize_to_xml(run: Run) -> str:
        """Serialize a Run object to XML string."""
        root = ET.Element('Run')
        root.set('version', run.version)
        
        game_icon_elem = ET.SubElement(root, 'GameIcon')
        game_icon_elem.text = run.game_icon
        
        game_name_elem = ET.SubElement(root, 'GameName')
        game_name_elem.text = run.game_name
        
        category_name_elem = ET.SubElement(root, 'CategoryName')
        category_name_elem.text = run.category_name
        
        layout_path_elem = ET.SubElement(root, 'LayoutPath')
        layout_path_elem.text = run.layout_path
        
        LSSSerializer._create_metadata_element(root, run.metadata)
        
        offset_elem = ET.SubElement(root, 'Offset')
        offset_elem.text = run.offset
        
        attempt_count_elem = ET.SubElement(root, 'AttemptCount')
        attempt_count_elem.text = str(run.attempt_count)
        
        # Attempt history
        attempt_history_elem = ET.SubElement(root, 'AttemptHistory')
        for attempt in run.attempt_history:
            LSSSerializer._create_attempt_element(attempt_history_elem, attempt)
        
        # Segments
        segments_elem = ET.SubElement(root, 'Segments')
        for segment in run.segments:
            LSSSerializer._create_segment_element(segments_elem, segment)
        
        # Auto splitter settings
        LSSSerializer._create_auto_splitter_settings_element(root, run.auto_splitter_settings)
        
        return ET.tostring(root, encoding='unicode')
    
    @staticmethod
    def serialize_to_pretty_xml(run: Run) -> str:
        """Serialize a Run object to pretty-formatted XML string."""
        xml_content = LSSSerializer.serialize_to_xml(run)
        
        # Pretty print the XML
        dom = minidom.parseString(xml_content)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Remove empty lines and fix encoding declaration
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
        
        return '\n'.join(lines) 