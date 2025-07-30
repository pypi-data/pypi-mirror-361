"""
Parser for LiveSplit LSS files.
"""

import xml.etree.ElementTree as ET
from typing import List, Optional

from .models import (Attempt, AutoSplitterSettings, Metadata, Run, Segment,
                     SegmentTime, SplitTime, Time)


class LSSParser:
    """Parser for LiveSplit .lss files."""
    
    @staticmethod
    def _parse_time_element(element: ET.Element) -> Time:
        """Parse a time element into a Time object."""
        time_data = {}
        
        real_time_elem = element.find('RealTime')
        if real_time_elem is not None:
            time_data['real_time'] = real_time_elem.text
            
        game_time_elem = element.find('GameTime')
        if game_time_elem is not None:
            time_data['game_time'] = game_time_elem.text
            
        pause_time_elem = element.find('PauseTime')
        if pause_time_elem is not None:
            time_data['pause_time'] = pause_time_elem.text
            
        return Time(**time_data)
    
    @staticmethod
    def _parse_metadata(metadata_elem: ET.Element) -> Metadata:
        """Parse metadata element into Metadata object."""
        metadata_data = {}
        
        run_elem = metadata_elem.find('Run')
        if run_elem is not None:
            metadata_data['run_id'] = run_elem.get('id', '')
            
        platform_elem = metadata_elem.find('Platform')
        if platform_elem is not None:
            metadata_data['platform'] = platform_elem.text or ''
            metadata_data['platform_uses_emulator'] = platform_elem.get('usesEmulator', 'False').lower() == 'true'
            
        region_elem = metadata_elem.find('Region')
        if region_elem is not None:
            metadata_data['region'] = region_elem.text or ''
            
        variables = {}
        variables_elem = metadata_elem.find('Variables')
        if variables_elem is not None:
            for var_elem in variables_elem:
                variables[var_elem.tag] = var_elem.text or ''
        metadata_data['variables'] = variables
                
        custom_variables = {}
        custom_variables_elem = metadata_elem.find('CustomVariables')
        if custom_variables_elem is not None:
            for var_elem in custom_variables_elem:
                custom_variables[var_elem.tag] = var_elem.text or ''
        metadata_data['custom_variables'] = custom_variables
                
        return Metadata(**metadata_data)
    
    @staticmethod
    def _parse_attempt(attempt_elem: ET.Element) -> Attempt:
        """Parse an attempt element into Attempt object."""
        attempt_data = {
            'id': attempt_elem.get('id', ''),
            'started': attempt_elem.get('started'),
            'is_started_synced': attempt_elem.get('isStartedSynced', 'True').lower() == 'true',
            'ended': attempt_elem.get('ended'),
            'is_ended_synced': attempt_elem.get('isEndedSynced', 'True').lower() == 'true',
            'time': LSSParser._parse_time_element(attempt_elem)
        }
        
        return Attempt(**attempt_data)
    
    @staticmethod
    def _parse_segment(segment_elem: ET.Element) -> Segment:
        """Parse a segment element into Segment object."""
        segment_data = {
            'name': segment_elem.find('Name').text or '',
            'icon': segment_elem.find('Icon').text or '',
            'split_times': [],
            'best_segment_time': Time(),
            'segment_history': []
        }
        
        # Parse split times
        split_times_elem = segment_elem.find('SplitTimes')
        if split_times_elem is not None:
            for split_time_elem in split_times_elem.findall('SplitTime'):
                split_time = SplitTime(
                    name=split_time_elem.get('name', ''),
                    time=LSSParser._parse_time_element(split_time_elem)
                )
                segment_data['split_times'].append(split_time)
        
        # Parse best segment time
        best_segment_elem = segment_elem.find('BestSegmentTime')
        if best_segment_elem is not None:
            segment_data['best_segment_time'] = LSSParser._parse_time_element(best_segment_elem)
        
        # Parse segment history
        segment_history_elem = segment_elem.find('SegmentHistory')
        if segment_history_elem is not None:
            for time_elem in segment_history_elem.findall('Time'):
                segment_time = SegmentTime(
                    id=time_elem.get('id', ''),
                    time=LSSParser._parse_time_element(time_elem)
                )
                segment_data['segment_history'].append(segment_time)
        
        return Segment(**segment_data)
    
    @staticmethod
    def _parse_auto_splitter_settings(settings_elem: Optional[ET.Element]) -> AutoSplitterSettings:
        """Parse auto splitter settings element."""
        settings_data = {}
        
        if settings_elem is None:
            return AutoSplitterSettings()
            
        auto_reset_elem = settings_elem.find('AutoReset')
        if auto_reset_elem is not None:
            settings_data['auto_reset'] = auto_reset_elem.text.lower() == 'true'
            
        set_high_priority_elem = settings_elem.find('SetHighPriority')
        if set_high_priority_elem is not None:
            settings_data['set_high_priority'] = set_high_priority_elem.text.lower() == 'true'
            
        set_game_time_elem = settings_elem.find('SetGameTime')
        if set_game_time_elem is not None:
            settings_data['set_game_time'] = set_game_time_elem.text.lower() == 'true'
            
        file_time_offset_elem = settings_elem.find('FileTimeOffset')
        if file_time_offset_elem is not None:
            settings_data['file_time_offset'] = file_time_offset_elem.text.lower() == 'true'
            
        splits = []
        splits_elem = settings_elem.find('Splits')
        if splits_elem is not None:
            for split_elem in splits_elem.findall('Split'):
                splits.append(split_elem.text or '')
        settings_data['splits'] = splits
                
        return AutoSplitterSettings(**settings_data)
    
    @staticmethod
    def parse_xml(xml_content: str) -> Run:
        """Parse XML content into a Run object."""
        root = ET.fromstring(xml_content)
        
        run_data = {
            'version': root.get('version', '1.7.0'),
            'game_name': root.find('GameName').text or '',
            'category_name': root.find('CategoryName').text or '',
            'layout_path': root.find('LayoutPath').text or '',
            'game_icon': root.find('GameIcon').text or '',
            'offset': root.find('Offset').text or '00:00:00',
            'attempt_count': int(root.find('AttemptCount').text or '0'),
            'attempt_history': [],
            'segments': [],
            'metadata': Metadata(),
            'auto_splitter_settings': AutoSplitterSettings()
        }
        
        # Parse metadata
        metadata_elem = root.find('Metadata')
        if metadata_elem is not None:
            run_data['metadata'] = LSSParser._parse_metadata(metadata_elem)
        
        # Parse attempt history
        attempt_history_elem = root.find('AttemptHistory')
        if attempt_history_elem is not None:
            for attempt_elem in attempt_history_elem.findall('Attempt'):
                run_data['attempt_history'].append(LSSParser._parse_attempt(attempt_elem))
        
        # Parse segments
        segments_elem = root.find('Segments')
        if segments_elem is not None:
            for segment_elem in segments_elem.findall('Segment'):
                run_data['segments'].append(LSSParser._parse_segment(segment_elem))
        
        # Parse auto splitter settings
        auto_splitter_elem = root.find('AutoSplitterSettings')
        run_data['auto_splitter_settings'] = LSSParser._parse_auto_splitter_settings(auto_splitter_elem)
        
        return Run(**run_data)         
        # Parse auto splitter settings
        auto_splitter_elem = root.find('AutoSplitterSettings')
        run_data['auto_splitter_settings'] = LSSParser._parse_auto_splitter_settings(auto_splitter_elem)
        
        return Run(**run_data) 