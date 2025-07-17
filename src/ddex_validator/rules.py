"""DDEX業務規則驗證"""

from typing import List, Optional, Dict, Set
from lxml import etree
from datetime import datetime
import re
from .models import ValidationIssue, SeverityLevel
from .constants import PATTERNS, ERROR_TYPES


class DDEXBusinessRules:
    """DDEX業務規則驗證器"""
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.namespace_map = {
            'ern': 'http://ddex.net/xml/ern/382',
            'ddex': 'http://ddex.net/xml/ddex/ern/382'
        }
    
    def validate_identifiers(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證識別碼格式"""
        issues = []
        
        # 驗證GRid
        grids = root.xpath(".//GRid | .//*[local-name()='GRid']")
        for grid in grids:
            if grid.text:
                if not PATTERNS["GRID"].match(grid.text.strip()):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的GRid格式: {grid.text}",
                        element_path=self._get_element_path(grid),
                        error_code="INVALID_GRID",
                        context=f"GRid值: '{grid.text.strip()}'",
                        suggestion="GRid格式應為: A1 + 5個字元 + 10個字元 + 1個字元 (例如: A1B2C3D4E5F6G7H8I9J0K1)"
                    ))
            else:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="GRid元素不能為空",
                    element_path=self._get_element_path(grid),
                    error_code="EMPTY_GRID",
                    suggestion="請提供有效的GRid值"
                ))
        
        # 驗證ISRC
        isrcs = root.xpath(".//ISRC | .//*[local-name()='ISRC']")
        for isrc in isrcs:
            if isrc.text:
                isrc_value = isrc.text.strip()
                if not PATTERNS["ISRC"].match(isrc_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的ISRC格式: {isrc_value}",
                        element_path=self._get_element_path(isrc),
                        error_code="INVALID_ISRC",
                        context=f"ISRC值: '{isrc_value}'",
                        suggestion="ISRC格式應為: 2個國家代碼 + 3個註冊者代碼 + 7個數字 (例如: USRC17607839)"
                    ))
                else:
                    # 驗證ISRC的邏輯結構
                    country_code = isrc_value[:2]
                    registrant_code = isrc_value[2:5]
                    year_code = isrc_value[5:7]
                    designation_code = isrc_value[7:12]
                    
                    # 檢查年份代碼是否合理
                    try:
                        year = int(year_code)
                        current_year = datetime.now().year % 100
                        if year > current_year + 10:  # 未來10年內
                            issues.append(ValidationIssue(
                                severity=SeverityLevel.WARNING,
                                message=f"ISRC年份代碼可能不正確: {year_code}",
                                element_path=self._get_element_path(isrc),
                                error_code="SUSPICIOUS_ISRC_YEAR",
                                context=f"年份代碼: {year_code}",
                                suggestion="請確認ISRC的年份代碼是否正確"
                            ))
                    except ValueError:
                        pass  # 已經在格式驗證中處理
            else:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="ISRC元素不能為空",
                    element_path=self._get_element_path(isrc),
                    error_code="EMPTY_ISRC",
                    suggestion="請提供有效的ISRC值"
                ))
        
        # 驗證ISAN
        isans = root.xpath(".//ISAN | .//*[local-name()='ISAN']")
        for isan in isans:
            if isan.text:
                isan_value = isan.text.strip().replace("-", "")  # 移除連字符
                if not PATTERNS["ISAN"].match(isan_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的ISAN格式: {isan.text}",
                        element_path=self._get_element_path(isan),
                        error_code="INVALID_ISAN",
                        context=f"ISAN值: '{isan.text.strip()}'",
                        suggestion="ISAN格式應為12個十六進制字符 (例如: 0000-3BAB-9352-0000)"
                    ))
        
        # 驗證V-ISAN
        visans = root.xpath(".//VISAN | .//*[local-name()='VISAN']")
        for visan in visans:
            if visan.text:
                visan_value = visan.text.strip().replace("-", "")  # 移除連字符
                if not PATTERNS["VISAN"].match(visan_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的V-ISAN格式: {visan.text}",
                        element_path=self._get_element_path(visan),
                        error_code="INVALID_VISAN",
                        context=f"V-ISAN值: '{visan.text.strip()}'",
                        suggestion="V-ISAN格式應為24個十六進制字符"
                    ))
        
        # 驗證ICPN (EAN/UPC)
        icpns = root.xpath(".//ICPN | .//*[local-name()='ICPN']")
        for icpn in icpns:
            if icpn.text:
                icpn_value = icpn.text.strip()
                if not PATTERNS["ICPN"].match(icpn_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的ICPN格式: {icpn_value}",
                        element_path=self._get_element_path(icpn),
                        error_code="INVALID_ICPN",
                        context=f"ICPN值: '{icpn_value}'",
                        suggestion="ICPN應為12位數字(UPC)或13位數字(EAN)"
                    ))
                else:
                    # 驗證校驗碼
                    if not self._validate_icpn_checksum(icpn_value):
                        issues.append(ValidationIssue(
                            severity=SeverityLevel.WARNING,
                            message=f"ICPN校驗碼可能不正確: {icpn_value}",
                            element_path=self._get_element_path(icpn),
                            error_code="INVALID_ICPN_CHECKSUM",
                            context=f"ICPN值: '{icpn_value}'",
                            suggestion="請檢查ICPN的校驗碼是否正確"
                        ))
        
        return issues
    
    def validate_durations(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證時間長度格式"""
        issues = []
        
        duration_elements = root.xpath(".//Duration | .//*[local-name()='Duration']")
        for duration in duration_elements:
            if duration.text:
                duration_value = duration.text.strip()
                if not PATTERNS["DURATION"].match(duration_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的時間長度格式: {duration_value}",
                        element_path=self._get_element_path(duration),
                        error_code="INVALID_DURATION",
                        context=f"Duration值: '{duration_value}'",
                        suggestion="時間長度格式應為ISO 8601 (例如: PT3M45S 表示3分45秒)"
                    ))
                else:
                    # 驗證時間長度的合理性
                    total_seconds = self._parse_duration_to_seconds(duration_value)
                    if total_seconds is not None:
                        if total_seconds > 7200:  # 超過2小時
                            issues.append(ValidationIssue(
                                severity=SeverityLevel.WARNING,
                                message=f"時間長度異常長: {duration_value} ({total_seconds}秒)",
                                element_path=self._get_element_path(duration),
                                error_code="UNUSUALLY_LONG_DURATION",
                                context=f"總秒數: {total_seconds}",
                                suggestion="請確認時間長度是否正確"
                            ))
                        elif total_seconds < 1:  # 少於1秒
                            issues.append(ValidationIssue(
                                severity=SeverityLevel.WARNING,
                                message=f"時間長度異常短: {duration_value}",
                                element_path=self._get_element_path(duration),
                                error_code="UNUSUALLY_SHORT_DURATION",
                                context=f"總秒數: {total_seconds}",
                                suggestion="請確認時間長度是否正確"
                            ))
        
        return issues
    
    def validate_dates(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證日期格式"""
        issues = []
        
        # 檢查各種日期元素
        date_elements = root.xpath(".//ReleaseDate | .//OriginalReleaseDate | .//CreationDate | "
                                 ".//StartDate | .//EndDate | .//*[local-name()='ReleaseDate'] | "
                                 ".//*[local-name()='OriginalReleaseDate'] | .//*[local-name()='CreationDate'] | "
                                 ".//*[local-name()='StartDate'] | .//*[local-name()='EndDate']")
        
        for date_elem in date_elements:
            if date_elem.text:
                date_value = date_elem.text.strip()
                if not PATTERNS["DATE"].match(date_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的日期格式: {date_value}",
                        element_path=self._get_element_path(date_elem),
                        error_code="INVALID_DATE",
                        context=f"日期值: '{date_value}'",
                        suggestion="日期格式應為YYYY-MM-DD或YYYY-MM或YYYY"
                    ))
                else:
                    # 驗證日期的合理性
                    if self._is_future_date(date_value):
                        tag_name = date_elem.tag.split('}')[-1] if '}' in date_elem.tag else date_elem.tag
                        if tag_name in ['CreationDate', 'OriginalReleaseDate']:
                            issues.append(ValidationIssue(
                                severity=SeverityLevel.WARNING,
                                message=f"{tag_name}是未來日期: {date_value}",
                                element_path=self._get_element_path(date_elem),
                                error_code="FUTURE_DATE",
                                context=f"日期值: '{date_value}'",
                                suggestion="請確認日期是否正確"
                            ))
        
        # 檢查DateTime格式
        datetime_elements = root.xpath(".//MessageCreatedDateTime | .//*[local-name()='MessageCreatedDateTime']")
        for dt_elem in datetime_elements:
            if dt_elem.text:
                dt_value = dt_elem.text.strip()
                if not PATTERNS["DATETIME"].match(dt_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"無效的日期時間格式: {dt_value}",
                        element_path=self._get_element_path(dt_elem),
                        error_code="INVALID_DATETIME",
                        context=f"DateTime值: '{dt_value}'",
                        suggestion="日期時間格式應為ISO 8601 (例如: 2024-01-15T10:30:00Z)"
                    ))
        
        return issues
    
    def validate_territories(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證地區代碼"""
        issues = []
        
        territories = root.xpath(".//Territory | .//TerritoryCode | .//*[local-name()='Territory'] | "
                               ".//*[local-name()='TerritoryCode']")
        
        for territory in territories:
            if territory.text:
                territory_value = territory.text.strip()
                if not PATTERNS["TERRITORY"].match(territory_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        message=f"可能無效的地區代碼: {territory_value}",
                        element_path=self._get_element_path(territory),
                        error_code="INVALID_TERRITORY",
                        context=f"地區代碼: '{territory_value}'",
                        suggestion="地區代碼應為ISO 3166-1 Alpha-2格式或'Worldwide'"
                    ))
        
        return issues
    
    def validate_languages(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證語言代碼"""
        issues = []
        
        # 檢查各種語言元素
        language_elements = root.xpath(".//LanguageOfPerformance | .//LanguageOfDubbing | "
                                     ".//LanguageOfSubtitles | .//*[local-name()='LanguageOfPerformance'] | "
                                     ".//*[local-name()='LanguageOfDubbing'] | .//*[local-name()='LanguageOfSubtitles']")
        
        for lang_elem in language_elements:
            if lang_elem.text:
                lang_value = lang_elem.text.strip()
                if not PATTERNS["LANGUAGE"].match(lang_value):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        message=f"可能無效的語言代碼: {lang_value}",
                        element_path=self._get_element_path(lang_elem),
                        error_code="INVALID_LANGUAGE",
                        context=f"語言代碼: '{lang_value}'",
                        suggestion="語言代碼應為ISO 639-1或ISO 639-2格式"
                    ))
        
        return issues
    
    def validate_required_elements(self, root: etree.Element, message_type: str) -> List[ValidationIssue]:
        """驗證必要元素"""
        issues = []
        
        if message_type == "NewReleaseMessage":
            # 檢查必要的MessageHeader
            if not root.xpath(".//MessageHeader | .//*[local-name()='MessageHeader']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="缺少必要的MessageHeader元素",
                    error_code="MISSING_MESSAGE_HEADER",
                    suggestion="NewReleaseMessage必須包含MessageHeader元素"
                ))
            else:
                # 檢查MessageHeader的必要子元素
                header = root.xpath(".//MessageHeader | .//*[local-name()='MessageHeader']")[0]
                required_header_elements = [
                    "MessageThreadId", "MessageId", "MessageSender", 
                    "MessageRecipient", "MessageCreatedDateTime"
                ]
                
                for req_elem in required_header_elements:
                    if not header.xpath(f".//{req_elem} | .//*[local-name()='{req_elem}']"):
                        issues.append(ValidationIssue(
                            severity=SeverityLevel.ERROR,
                            message=f"MessageHeader缺少必要元素: {req_elem}",
                            element_path="MessageHeader",
                            error_code="MISSING_HEADER_ELEMENT",
                            context=f"缺少元素: {req_elem}",
                            suggestion=f"請在MessageHeader中添加{req_elem}元素"
                        ))
            
            # 檢查必要的ReleaseList
            if not root.xpath(".//ReleaseList | .//*[local-name()='ReleaseList']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="缺少必要的ReleaseList元素",
                    error_code="MISSING_RELEASE_LIST",
                    suggestion="NewReleaseMessage必須包含ReleaseList元素"
                ))
            
            # 檢查必要的ResourceList
            if not root.xpath(".//ResourceList | .//*[local-name()='ResourceList']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    message="建議包含ResourceList元素",
                    error_code="MISSING_RESOURCE_LIST",
                    suggestion="通常NewReleaseMessage應該包含ResourceList元素"
                ))
        
        elif message_type == "CatalogListMessage":
            # 檢查CatalogListMessage的必要元素
            if not root.xpath(".//MessageHeader | .//*[local-name()='MessageHeader']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="缺少必要的MessageHeader元素",
                    error_code="MISSING_MESSAGE_HEADER",
                    suggestion="CatalogListMessage必須包含MessageHeader元素"
                ))
        
        return issues
    
    def validate_business_logic(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證業務邏輯"""
        issues = []
        
        # 檢查Release是否有ResourceList或ResourceGroupList
        releases = root.xpath(".//Release | .//*[local-name()='Release']")
        for release in releases:
            has_resources = bool(release.xpath(".//ResourceList | .//ResourceGroupList | "
                                             ".//*[local-name()='ResourceList'] | "
                                             ".//*[local-name()='ResourceGroupList']"))
            has_resource_refs = bool(release.xpath(".//ReleaseResourceReference | "
                                                 ".//*[local-name()='ReleaseResourceReference']"))
            
            if not has_resources and not has_resource_refs:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    message="Release缺少ResourceList、ResourceGroupList或ReleaseResourceReference",
                    element_path=self._get_element_path(release),
                    error_code="MISSING_RESOURCES",
                    suggestion="Release應該包含資源引用或資源列表"
                ))
        
        # 檢查SoundRecording是否有Duration
        sound_recordings = root.xpath(".//SoundRecording | .//*[local-name()='SoundRecording']")
        for sr in sound_recordings:
            if not sr.xpath(".//Duration | .//*[local-name()='Duration']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    message="SoundRecording建議包含Duration",
                    element_path=self._get_element_path(sr),
                    error_code="MISSING_DURATION",
                    suggestion="為了更好的用戶體驗，建議為SoundRecording提供Duration"
                ))
        
        # 檢查Deal的有效性
        deals = root.xpath(".//Deal | .//*[local-name()='Deal']")
        for deal in deals:
            # 檢查是否有UseType
            if not deal.xpath(".//UseType | .//*[local-name()='UseType']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="Deal缺少UseType",
                    element_path=self._get_element_path(deal),
                    error_code="MISSING_USE_TYPE",
                    suggestion="每個Deal必須指定UseType"
                ))
            
            # 檢查是否有Territory
            if not deal.xpath(".//TerritoryCode | .//Territory | "
                            ".//*[local-name()='TerritoryCode'] | .//*[local-name()='Territory']"):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message="Deal缺少Territory",
                    element_path=self._get_element_path(deal),
                    error_code="MISSING_TERRITORY",
                    suggestion="每個Deal必須指定適用的Territory"
                ))
        
        # 檢查資源引用的一致性
        issues.extend(self._validate_resource_references(root))
        
        # 檢查重複的識別碼
        issues.extend(self._validate_duplicate_identifiers(root))
        
        return issues
    
    def validate_technical_details(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證技術細節"""
        issues = []
        
        # 檢查音頻技術細節
        audio_details = root.xpath(".//TechnicalSoundRecordingDetails | "
                                 ".//*[local-name()='TechnicalSoundRecordingDetails']")
        for details in audio_details:
            # 檢查BitRate
            bitrates = details.xpath(".//BitRate | .//*[local-name()='BitRate']")
            for bitrate in bitrates:
                if bitrate.text:
                    try:
                        br_value = float(bitrate.text)
                        if br_value < 64 or br_value > 320:
                            issues.append(ValidationIssue(
                                severity=SeverityLevel.WARNING,
                                message=f"音頻BitRate可能不合理: {br_value}",
                                element_path=self._get_element_path(bitrate),
                                error_code="UNUSUAL_BITRATE",
                                context=f"BitRate值: {br_value}",
                                suggestion="音頻BitRate通常在64-320 kbps範圍內"
                            ))
                    except ValueError:
                        issues.append(ValidationIssue(
                            severity=SeverityLevel.ERROR,
                            message=f"無效的BitRate值: {bitrate.text}",
                            element_path=self._get_element_path(bitrate),
                            error_code="INVALID_BITRATE",
                            suggestion="BitRate應為數字值"
                        ))
        
        return issues
    
    def _validate_resource_references(self, root: etree.Element) -> List[ValidationIssue]:
        """驗證資源引用的一致性"""
        issues = []
        
        # 收集所有資源引用
        resource_refs = set()
        ref_elements = root.xpath(".//ReleaseResourceReference | .//ResourceReference | "
                                ".//*[local-name()='ReleaseResourceReference'] | "
                                ".//*[local-name()='ResourceReference']")
        
        for ref_elem in ref_elements:
            if ref_elem.text:
                resource_refs.add(ref_elem.text.strip())
        
        # 收集所有資源定義
        resource_anchors = set()
        anchor_elements = root.xpath(".//*[@ResourceReference] | .//*[local-name()='ResourceReference']")
        
        for anchor_elem in anchor_elements:
            anchor_value = anchor_elem.get('ResourceReference')
            if anchor_value:
                resource_anchors.add(anchor_value)
        
        # 檢查未定義的引用
        undefined_refs = resource_refs - resource_anchors
        for undefined_ref in undefined_refs:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                message=f"引用了未定義的資源: {undefined_ref}",
                error_code="UNDEFINED_RESOURCE_REFERENCE",
                context=f"資源引用: {undefined_ref}",
                suggestion="請確認資源引用對應的資源已定義"
            ))
        
        # 檢查未使用的資源
        unused_anchors = resource_anchors - resource_refs
        for unused_anchor in unused_anchors:
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                message=f"定義了未使用的資源: {unused_anchor}",
                error_code="UNUSED_RESOURCE",
                context=f"資源錨點: {unused_anchor}",
                suggestion="考慮移除未使用的資源定義"
            ))
        
        return issues
    
    def _validate_duplicate_identifiers(self, root: etree.Element) -> List[ValidationIssue]:
        """檢查重複的識別碼"""
        issues = []
        
        # 檢查重複的ISRC
        isrc_values = {}
        isrcs = root.xpath(".//ISRC | .//*[local-name()='ISRC']")
        for isrc in isrcs:
            if isrc.text:
                isrc_value = isrc.text.strip()
                if isrc_value in isrc_values:
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"重複的ISRC: {isrc_value}",
                        element_path=self._get_element_path(isrc),
                        error_code="DUPLICATE_ISRC",
                        context=f"ISRC值: '{isrc_value}'",
                        suggestion="每個ISRC在訊息中應該是唯一的"
                    ))
                else:
                    isrc_values[isrc_value] = isrc
        
        # 檢查重複的GRid
        grid_values = {}
        grids = root.xpath(".//GRid | .//*[local-name()='GRid']")
        for grid in grids:
            if grid.text:
                grid_value = grid.text.strip()
                if grid_value in grid_values:
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"重複的GRid: {grid_value}",
                        element_path=self._get_element_path(grid),
                        error_code="DUPLICATE_GRID",
                        context=f"GRid值: '{grid_value}'",
                        suggestion="每個GRid在訊息中應該是唯一的"
                    ))
                else:
                    grid_values[grid_value] = grid
        
        return issues
    
    def _get_element_path(self, element: etree.Element) -> str:
        """取得元素的XPath路徑"""
        path_parts = []
        current = element
        
        while current is not None:
            tag = current.tag
            if '}' in tag:
                tag = tag.split('}')[1]  # 移除命名空間
            
            # 計算同名兄弟元素的位置
            if current.getparent() is not None:
                siblings = [e for e in current.getparent() if e.tag == current.tag]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    tag = f"{tag}[{index}]"
            
            path_parts.insert(0, tag)
            current = current.getparent()
        
        return "/" + "/".join(path_parts)
    
    def _validate_icpn_checksum(self, icpn: str) -> bool:
        """驗證ICPN(EAN/UPC)校驗碼"""
        try:
            if len(icpn) == 12:  # UPC
                # UPC校驗碼算法
                odd_sum = sum(int(icpn[i]) for i in range(0, 11, 2))
                even_sum = sum(int(icpn[i]) for i in range(1, 11, 2))
                total = odd_sum * 3 + even_sum
                check_digit = (10 - (total % 10)) % 10
                return check_digit == int(icpn[11])
            
            elif len(icpn) == 13:  # EAN
                # EAN校驗碼算法
                odd_sum = sum(int(icpn[i]) for i in range(0, 12, 2))
                even_sum = sum(int(icpn[i]) for i in range(1, 12, 2))
                total = odd_sum + even_sum * 3
                check_digit = (10 - (total % 10)) % 10
                return check_digit == int(icpn[12])
            
            return False
        except (ValueError, IndexError):
            return False
    
    def _parse_duration_to_seconds(self, duration: str) -> Optional[float]:
        """將ISO 8601時間長度轉換為秒數"""
        try:
            # 移除PT前綴
            if not duration.startswith('PT'):
                return None
            
            duration = duration[2:]
            
            # 解析小時、分鐘、秒
            hours = 0
            minutes = 0
            seconds = 0.0
            
            # 匹配小時
            hour_match = re.search(r'(\d+)H', duration)
            if hour_match:
                hours = int(hour_match.group(1))
            
            # 匹配分鐘
            minute_match = re.search(r'(\d+)M', duration)
            if minute_match:
                minutes = int(minute_match.group(1))
            
            # 匹配秒
            second_match = re.search(r'([\d.]+)S', duration)
            if second_match:
                seconds = float(second_match.group(1))
            
            return hours * 3600 + minutes * 60 + seconds
        
        except (ValueError, AttributeError):
            return None
    
    def _is_future_date(self, date_str: str) -> bool:
        """檢查是否為未來日期"""
        try:
            from datetime import datetime
            
            # 解析不同格式的日期
            if len(date_str) == 4:  # YYYY
                date_obj = datetime.strptime(date_str, '%Y')
            elif len(date_str) == 7:  # YYYY-MM
                date_obj = datetime.strptime(date_str, '%Y-%m')
            elif len(date_str) == 10:  # YYYY-MM-DD
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                return False
            
            return date_obj.date() > datetime.now().date()
        
        except ValueError:
            return False

