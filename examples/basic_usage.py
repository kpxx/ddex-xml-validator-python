#!/usr/bin/env python3
"""基本使用範例"""

import sys
import os

# 添加src目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ddex_validator.validator import DDEXXMLValidator


def main():
    # 建立驗證器
    validator = DDEXXMLValidator(
        schema_path="schemas/ddex/3.8.2/ddex_3-8-2.xsd"  # 指定XSD檔案路徑
    )
    
    # 範例XML內容
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<NewReleaseMessage xmlns="http://ddex.net/xml/ern/382" 
                   MessageSchemaVersionId="3.8.2" 
                   BusinessProfileVersionId="CommonReleaseTypes/14" 
                   ReleaseProfileVersionId="CommonReleaseTypes/14">
    <MessageHeader>
        <MessageThreadId>MSG_001</MessageThreadId>
        <MessageId>MSG_001_001</MessageId>
        <MessageSender>
            <PartyId>PADPIDA2014120301R</PartyId>
            <PartyName>
                <FullName>Test Sender</FullName>
            </PartyName>
        </MessageSender>
        <MessageRecipient>
            <PartyId>PADPIDA2014120302R</PartyId>
            <PartyName>
                <FullName>Test Recipient</FullName>
            </PartyName>
        </MessageRecipient>
        <MessageCreatedDateTime>2024-01-15T10:30:00Z</MessageCreatedDateTime>
        <MessageControlType>LiveMessage</MessageControlType>
    </MessageHeader>
    
    <ResourceList>
        <SoundRecording>
            <SoundRecordingType>MusicalWorkSoundRecording</SoundRecordingType>
            <SoundRecordingId>
                <ISRC>USRC17607839</ISRC>
            </SoundRecordingId>
            <ResourceReference>A1</ResourceReference>
            <ReferenceTitle>
                <TitleText>Test Song</TitleText>
            </ReferenceTitle>
            <Duration>PT3M45S</Duration>
            <SoundRecordingDetailsByTerritory>
                <TerritoryCode>Worldwide</TerritoryCode>
                <Title>
                    <TitleText>Test Song</TitleText>
                </Title>
                <DisplayArtist>
                    <PartyName>
                        <FullName>Test Artist</FullName>
                    </PartyName>
                </DisplayArtist>
            </SoundRecordingDetailsByTerritory>
        </SoundRecording>
    </ResourceList>
    
    <ReleaseList>
        <Release>
            <ReleaseId>
                <GRid>A1B2C3D4E5F6G7H8I9J0K1</GRid>
            </ReleaseId>
            <ReleaseReference>R1</ReleaseReference>
            <ReferenceTitle>
                <TitleText>Test Album</TitleText>
            </ReferenceTitle>
            <ReleaseResourceReferenceList>
                <ReleaseResourceReference>A1</ReleaseResourceReference>
            </ReleaseResourceReferenceList>
            <ReleaseType>Album</ReleaseType>
            <ReleaseDetailsByTerritory>
                <TerritoryCode>Worldwide</TerritoryCode>
                <DisplayArtistName>Test Artist</DisplayArtistName>
                <LabelName>Test Label</LabelName>
                <Title>
                    <TitleText>Test Album</TitleText>
                </Title>
                <Genre>
                    <GenreText>Pop</GenreText>
                </Genre>
                <ReleaseDate>2024-01-15</ReleaseDate>
            </ReleaseDetailsByTerritory>
        </Release>
    </ReleaseList>
    
    <DealList>
        <ReleaseDeal>
            <DealReleaseReference>R1</DealReleaseReference>
            <Deal>
                <DealTerms>
                    <CommercialModelType>SubscriptionModel</CommercialModelType>
                    <Usage>
                        <UseType>Stream</UseType>
                    </Usage>
                    <TerritoryCode>Worldwide</TerritoryCode>
                    <ValidityPeriod>
                        <StartDate>2024-01-15</StartDate>
                    </ValidityPeriod>
                </DealTerms>
            </Deal>
        </ReleaseDeal>
    </DealList>
</NewReleaseMessage>"""
    
    # 驗證XML
    print("開始驗證DDEX XML...")
    result = validator.validate_string(sample_xml)
    
    # 顯示結果
    result.print_summary()
    
    # 如果有檔案，也可以驗證檔案
    # result = validator.validate_file("path/to/your/ern_message.xml")


if __name__ == "__main__":
    main()

